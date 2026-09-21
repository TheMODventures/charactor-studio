"""Disposable database + actual API/worker for browser tests. Does not load ML models."""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix="character-e2e-") as folder:
    env = {
        **os.environ,
        "PYTHONPATH": str(root / "backend"),
        "DATABASE_URL": "sqlite:///" + folder + "/app.db",
        "ASSETS_DIR": folder + "/assets",
        "SEED_CHARACTERS": "true",
        "SPEECH_URL": "",
        "VIDEO_URL": "",
    }
    subprocess.run(
        [sys.executable, "-c", "from app.bootstrap import initialize; initialize()"],
        env=env,
        check=True,
    )
    api = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        env=env,
        cwd=root,
    )
    worker = subprocess.Popen(
        [sys.executable, "-m", "app.generations.generation_worker"], env=env, cwd=root
    )
    try:
        while api.poll() is None and worker.poll() is None:
            time.sleep(0.5)
    finally:
        for process in (api, worker):
            process.terminate()
        for process in (api, worker):
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
