"""Private Kokoro + SadTalker service; GPU inference runs in SadTalker's venv."""

import io
import math
import os
import secrets
import subprocess
import tempfile
import threading
import wave
from functools import lru_cache
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI(title="Kokoro and SadTalker")
lock = threading.Lock()
VOICES = {"af_heart", "af_bella"}


def authorize(value):
    token = os.getenv("PROVIDER_TOKEN", "")
    if not token or not secrets.compare_digest(value, "Bearer " + token):
        raise HTTPException(401, "Provider authorization required")


def run(command, timeout=120, cwd=None):
    try:
        subprocess.run(command, check=True, timeout=timeout, cwd=cwd)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        raise HTTPException(
            500, "Rendering failed; inspect model service logs"
        ) from exc


def sad_config():
    return Path(os.getenv("SADTALKER_ROOT", "/opt/SadTalker")), os.getenv(
        "SADTALKER_PYTHON", "/opt/sadtalker-venv/bin/python"
    )


@lru_cache
def check_runtime():
    root, python = sad_config()
    result = subprocess.run(
        [
            python,
            "-c",
            "import torch; import src.utils.preprocess; "
            "raise SystemExit(0 if torch.cuda.is_available() else 1)",
        ],
        cwd=root,
        capture_output=True,
        timeout=30,
    )
    if result.returncode:
        raise HTTPException(
            503, "SadTalker requires its installed dependencies and an NVIDIA GPU"
        )
    # Load CPU speech weights once; failures leave rendering unavailable.
    kokoro()
    return True


@lru_cache
def kokoro():
    from kokoro import KPipeline

    # Save GPU memory for animation. Downloads the public weights on first use.
    return KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M", device="cpu")


@app.get("/health")
def health(authorization: str = Header(default="")):
    authorize(authorization)
    root, python = sad_config()
    required = [
        root / "inference.py",
        Path(python),
        root / "checkpoints/SadTalker_V0.0.2_256.safetensors",
        root / "checkpoints/mapping_00109-model.pth.tar",
    ]
    if not all(p.is_file() for p in required):
        raise HTTPException(503, "Install SadTalker environment and checkpoints")
    with lock:
        check_runtime()
    return {"status": "ok", "model": "kokoro+sadtalker", "inference_verified": False}


@app.post("/synthesize")
def synthesize(
    text: str = Form(...),
    voice: str = Form(...),
    authorization: str = Header(default=""),
):
    authorize(authorization)
    if voice not in VOICES or not text.strip() or len(text) > 1500:
        raise HTTPException(
            422, "Use a built-in voice and 1–1500 characters of dialogue"
        )
    import numpy as np
    import soundfile as sf

    with lock:
        chunks = [audio.numpy() for _, _, audio in kokoro()(text, voice=voice, speed=1)]
        if not chunks:
            raise HTTPException(422, "No speech was generated")
        output = io.BytesIO()
        sf.write(output, np.concatenate(chunks), 24000, format="WAV", subtype="PCM_16")
        return Response(output.getvalue(), media_type="audio/wav")


def save_upload(upload, path):
    data = upload.file.read(30 * 1024 * 1024 + 1)
    if len(data) > 30 * 1024 * 1024:
        raise HTTPException(413, "Media too large")
    path.write_bytes(data)


def wav_duration(path):
    try:
        with wave.open(str(path), "rb") as audio:
            if (audio.getnchannels(), audio.getsampwidth(), audio.getframerate()) != (
                1,
                2,
                24000,
            ):
                raise ValueError("Expected mono PCM 24 kHz")
            return audio.getnframes() / audio.getframerate()
    except (wave.Error, ValueError, EOFError) as exc:
        raise HTTPException(422, "Expected mono 24 kHz PCM WAV") from exc


@app.post("/generate")
def generate(
    image: UploadFile = File(...),
    audio1: UploadFile = File(...),
    audio2: UploadFile = File(...),
    prompt: str = Form(""),
    authorization: str = Header(default=""),
):
    authorize(authorization)
    health(authorization)
    root, python = sad_config()
    import imageio_ffmpeg

    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    with lock, tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        scene = folder / "scene.png"
        save_upload(image, scene)
        tracks = [folder / "left.wav", folder / "right.wav"]
        for upload, path in zip([audio1, audio2], tracks):
            save_upload(upload, path)
        lengths = [wav_duration(path) for path in tracks]
        duration = lengths[0]
        if not 1 <= duration <= 65 or abs(duration - lengths[1]) > 0.04:
            raise HTTPException(
                422, "Supply two aligned tracks of equal length, up to 65 seconds"
            )
        portraits = []
        for side in range(2):
            portrait = folder / f"portrait-{side}.png"
            # Isolate each face from the supplied fixed image, retaining its background.
            run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(scene),
                    "-vf",
                    f"crop=trunc(iw/4)*2:trunc(ih/2)*2:{'0' if side == 0 else 'iw-ow'}:0",
                    "-frames:v",
                    "1",
                    str(portrait),
                ]
            )
            portraits.append(portrait)
        segments = []
        # Bound per-inference frame memory; both speakers share the same clock.
        for index in range(math.ceil(duration / 10)):
            start = index * 10
            seconds = min(10, duration - start)
            clips = []
            for side in range(2):
                audio = folder / f"chunk-{index}-{side}.wav"
                run(
                    [
                        ffmpeg,
                        "-y",
                        "-i",
                        str(tracks[side]),
                        "-ss",
                        str(start),
                        "-t",
                        str(seconds),
                        "-c:a",
                        "pcm_s16le",
                        str(audio),
                    ]
                )
                results = folder / f"result-{index}-{side}"
                results.mkdir()
                run(
                    [
                        python,
                        str(root / "inference.py"),
                        "--source_image",
                        str(portraits[side]),
                        "--driven_audio",
                        str(audio),
                        "--checkpoint_dir",
                        str(root / "checkpoints"),
                        "--result_dir",
                        str(results),
                        "--size",
                        "256",
                        "--batch_size",
                        "1",
                        "--preprocess",
                        "full",
                        "--still",
                    ],
                    timeout=int(os.getenv("VIDEO_TIMEOUT", "3600")),
                    cwd=root,
                )
                outputs = list(results.glob("*.mp4"))
                if len(outputs) != 1:
                    raise HTTPException(
                        500, "SadTalker did not produce the expected clip"
                    )
                clips.append(outputs[0])
            segment = folder / f"segment-{index}.mp4"
            filters = (
                ";".join(
                    f"[{side}:v]scale=480:540:force_original_aspect_ratio=decrease,"
                    f"pad=480:540:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=25,"
                    f"tpad=stop_mode=clone:stop_duration=1[v{side}]"
                    for side in range(2)
                )
                + ";[v0][v1]hstack=inputs=2[out]"
            )
            run(
                [
                    ffmpeg,
                    "-y",
                    "-i",
                    str(clips[0]),
                    "-i",
                    str(clips[1]),
                    "-filter_complex",
                    filters,
                    "-map",
                    "[out]",
                    "-an",
                    "-t",
                    str(seconds),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "fast",
                    "-pix_fmt",
                    "yuv420p",
                    str(segment),
                ]
            )
            segments.append(segment)
        manifest = folder / "segments.txt"
        manifest.write_text("".join(f"file '{p.name}'\n" for p in segments))
        output = folder / "conversation.mp4"
        run(
            [
                ffmpeg,
                "-y",
                "-f",
                "concat",
                "-safe",
                "1",
                "-i",
                str(manifest),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
        return Response(output.read_bytes(), media_type="video/mp4")
