import os
from pathlib import Path
from tempfile import TemporaryDirectory

_storage = TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_storage.name) / "test.db")
os.environ["ASSETS_DIR"] = str(Path(_storage.name) / "assets")
os.environ["SEED_CHARACTERS"] = "true"
os.environ["FIXED_DEMO_MODE"] = "false"
os.environ["ENABLE_ANIMATED_RENDERS"] = "false"
os.environ["SPEECH_URL"] = ""
os.environ["VIDEO_URL"] = ""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
