"""Run inside Chatterbox's own environment, on a private GPU service."""

import os
import secrets
import tempfile
import threading
from pathlib import Path
from functools import lru_cache
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response

app = FastAPI(title="Chatterbox adapter")
lock = threading.Lock()


def authorize(authorization):
    token = os.environ.get("PROVIDER_TOKEN", "")
    if not token or not secrets.compare_digest(authorization, "Bearer " + token):
        raise HTTPException(401, "Provider authorization required")


@lru_cache
def get_model():
    from chatterbox.tts import ChatterboxTTS

    return ChatterboxTTS.from_pretrained(device=os.environ.get("TTS_DEVICE", "cuda"))


@app.get("/health")
def health(authorization: str = Header(default="")):
    authorize(authorization)
    return {
        "status": "ok",
        "model": "chatterbox",
        "loaded": get_model.cache_info().currsize > 0,
    }


@app.post("/synthesize")
def synthesize(
    reference: UploadFile = File(...),
    text: str = Form(...),
    expressiveness: float = Form(0.5),
    authorization: str = Header(default=""),
):
    authorize(authorization)
    if not 1 <= len(text) <= 1500 or not 0 <= expressiveness <= 1:
        raise HTTPException(422, "Invalid speech request")
    data = reference.file.read(20 * 1024 * 1024 + 1)
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "Reference too large")
    import torchaudio

    with lock, tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "reference.wav"
        path.write_bytes(data)
        model = get_model()
        audio = model.generate(
            text,
            audio_prompt_path=str(path),
            exaggeration=expressiveness,
            cfg_weight=0.5,
        )
        output = Path(folder) / "speech.wav"
        torchaudio.save(str(output), audio, model.sr)
        return Response(output.read_bytes(), media_type="audio/wav")
