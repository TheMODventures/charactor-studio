"""HTTP adapter for the official InfiniteTalk CLI. Run in its CUDA environment."""

import json
import os
import secrets
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI(title="InfiniteTalk adapter")
lock = threading.Lock()


def authorize(authorization):
    token = os.environ.get("PROVIDER_TOKEN", "")
    if not token or not secrets.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "Provider authorization required")


def config():
    root = Path(os.environ.get("INFINITETALK_ROOT", "/opt/InfiniteTalk"))
    weights = Path(os.environ.get("VIDEO_WEIGHTS_DIR", str(root / "weights")))
    return root, weights


@app.get("/health")
def health(authorization: str = Header(default="")):
    authorize(authorization)
    root, weights = config()
    required = [
        root / "generate_infinitetalk.py",
        weights / "Wan2.1-I2V-14B-480P",
        weights / "chinese-wav2vec2-base",
        weights / "InfiniteTalk/multi/infinitetalk.safetensors",
    ]
    if not all(p.exists() for p in required):
        raise HTTPException(503, "Install InfiniteTalk and all model weights first")
    return {"status": "ok", "model": "infinitetalk", "inference_verified": False}


@app.post("/generate")
def generate(
    image: UploadFile = File(...),
    audio1: UploadFile = File(...),
    audio2: UploadFile = File(...),
    prompt: str = Form(...),
    authorization: str = Header(default=""),
):
    authorize(authorization)
    root, weights = config()
    if len(prompt) > 16000:
        raise HTTPException(422, "Prompt too long")
    with lock, tempfile.TemporaryDirectory() as folder:
        folder = Path(folder)
        for name, upload in [
            ("scene.jpg", image),
            ("person1.wav", audio1),
            ("person2.wav", audio2),
        ]:
            data = upload.file.read(30 * 1024 * 1024 + 1)
            if len(data) > 30 * 1024 * 1024:
                raise HTTPException(413, "Media too large")
            (folder / name).write_bytes(data)
        manifest = {
            "prompt": prompt,
            "cond_video": str(folder / "scene.jpg"),
            "audio_type": "para",
            "cond_audio": {
                "person1": str(folder / "person1.wav"),
                "person2": str(folder / "person2.wav"),
            },
        }
        (folder / "input.json").write_text(json.dumps(manifest))
        command = [
            sys.executable,
            str(root / "generate_infinitetalk.py"),
            "--ckpt_dir",
            str(weights / "Wan2.1-I2V-14B-480P"),
            "--wav2vec_dir",
            str(weights / "chinese-wav2vec2-base"),
            "--infinitetalk_dir",
            str(weights / "InfiniteTalk/multi/infinitetalk.safetensors"),
            "--input_json",
            str(folder / "input.json"),
            "--size",
            "infinitetalk-480",
            "--sample_steps",
            "40",
            "--mode",
            "streaming",
            "--motion_frame",
            "9",
            "--num_persistent_param_in_dit",
            "0",
            "--save_file",
            str(folder / "render"),
        ]
        try:
            subprocess.run(
                command,
                cwd=root,
                check=True,
                timeout=int(os.getenv("VIDEO_TIMEOUT", "3600")),
            )
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            raise HTTPException(
                500, "InfiniteTalk failed; inspect private service logs"
            ) from exc
        output = folder / "render.mp4"
        if not output.exists():
            raise HTTPException(500, "Model did not produce the expected MP4")
        return Response(output.read_bytes(), media_type="video/mp4")
