"""Run one API process and one worker. Model services are deployed separately."""

import os
import signal
import subprocess
import sys
import time
import secrets
from pathlib import Path

root = Path(__file__).resolve().parents[1]
env = {**os.environ, "PYTHONPATH": str(root / "backend")}
bundled_models = os.getenv("START_MODEL_SERVICE", "false").lower() == "true"
if bundled_models:
    env["PROVIDER_TOKEN"] = env.get("PROVIDER_TOKEN") or secrets.token_urlsafe(32)
    env["SPEECH_URL"] = "http://127.0.0.1:8001"
    env["VIDEO_URL"] = "http://127.0.0.1:8001"
    env["SPEECH_PROVIDER"] = "kokoro"
    env["VIDEO_PROVIDER"] = "sadtalker"
subprocess.run(
    [sys.executable, "-c", "from app.bootstrap import initialize; initialize()"],
    env=env,
    check=True,
)
processes = []


def stop(*args):
    for process in processes:
        if process.poll() is None:
            process.terminate()
    for process in processes:
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
    sys.exit(0)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)
if bundled_models:
    processes.append(
        subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "model_services.lightweight_service:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8001",
            ],
            env=env,
            cwd=root,
        )
    )
processes.append(
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            os.getenv("HOST", "127.0.0.1"),
            "--port",
            os.getenv("PORT", "8000"),
        ],
        env=env,
        cwd=root,
    )
)
processes.append(
    subprocess.Popen(
        [sys.executable, "-m", "app.generations.generation_worker"], env=env, cwd=root
    )
)
while all(p.poll() is None for p in processes):
    time.sleep(1)
stop()
