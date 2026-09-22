from io import BytesIO
from PIL import Image
from app.generations.generation_worker import claim_job, run_generation
from app.shared.audio_service import AudioService, wav_write, RATE
from array import array
import pytest


def upload_image(client):
    image = BytesIO()
    Image.new("RGB", (640, 360), "#b7a9c8").save(image, format="PNG")
    response = client.post(
        "/api/v1/assets",
        files={"file": ("fictional-test.png", image.getvalue(), "image/png")},
        data={
            "kind": "image",
            "rights": "original",
            "rights_note": "Synthetic test image owned by this test suite",
            "consent": "true",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def setup_project(client):
    characters = client.get("/api/v1/characters").json()
    ids = [c["id"] for c in characters[:2]]
    script = client.post(
        "/api/v1/conversations",
        json={
            "title": "Exact words test",
            "approved": True,
            "turns": [
                {"character_id": ids[0], "text": "Don't change my words."},
                {"character_id": ids[1], "text": "Of course, I won't."},
            ],
        },
    ).json()
    scene = client.post(
        "/api/v1/scenes",
        json={
            "name": "Test room",
            "image_asset_id": upload_image(client),
            "character_ids": ids,
            "approved": True,
        },
    ).json()
    return script, scene


def test_character_roundtrip(client):
    original = client.get("/api/v1/characters/royale").json()
    original["profile"]["region"] = "Creator-defined Atlanta influence"
    result = client.put("/api/v1/characters/royale", json=original)
    assert result.status_code == 200
    assert result.json()["version"] == original["version"] + 1
    assert (
        client.get("/api/v1/characters/royale").json()["profile"]["region"]
        == original["profile"]["region"]
    )


def test_validation_and_consent(client):
    assert client.get("/api/v1/characters/missing").status_code == 404
    result = client.post(
        "/api/v1/assets",
        files={"file": ("x.png", b"invalid", "image/png")},
        data={
            "kind": "image",
            "rights": "original",
            "rights_note": "Owned test",
            "consent": "false",
        },
    )
    assert result.status_code == 422
    result = client.post(
        "/api/v1/assets",
        files={"file": ("x.png", b"invalid", "image/png")},
        data={
            "kind": "image",
            "rights": "original",
            "rights_note": "Owned test",
            "consent": "true",
        },
    )
    assert result.status_code == 422
    assert (
        client.post(
            "/api/v1/scenes",
            json={
                "name": "Bad",
                "image_asset_id": upload_image(client),
                "character_ids": ["royale", "royale"],
            },
        ).status_code
        == 422
    )


def test_script_approval_and_snapshot(client):
    script, scene = setup_project(client)
    script["approved"] = False
    client.put(f"/api/v1/conversations/{script['id']}", json=script)
    data = {
        "conversation_id": script["id"],
        "scene_id": scene["id"],
        "kind": "storyboard",
        "target_seconds": 10,
    }
    assert client.post("/api/v1/generations", json=data).status_code == 422
    script["approved"] = True
    client.put(f"/api/v1/conversations/{script['id']}", json=script)
    job = client.post("/api/v1/generations", json=data).json()
    script["turns"][0]["text"] = "A changed script."
    client.put(f"/api/v1/conversations/{script['id']}", json=script)
    saved = client.get(f"/api/v1/generations/{job['id']}").json()
    assert (
        saved["settings"]["conversation"]["turns"][0]["text"]
        == "Don't change my words."
    )
    assert client.post(f"/api/v1/generations/{job['id']}/cancel").status_code == 200
    assert client.post(f"/api/v1/generations/{job['id']}/cancel").status_code == 409


def test_real_storyboard_render(client):
    script, scene = setup_project(client)
    response = client.post(
        "/api/v1/generations",
        json={
            "conversation_id": script["id"],
            "scene_id": scene["id"],
            "target_seconds": 10,
            "kind": "storyboard",
        },
    )
    assert response.status_code == 201
    job_id = response.json()["id"]
    assert claim_job() == job_id
    assert claim_job() is None
    run_generation(job_id)
    job = client.get(f"/api/v1/generations/{job_id}").json()
    assert job["status"] == "completed", job
    assert 0 < job["duration"] < 10
    video = client.get(f"/api/v1/assets/{job['output_asset_id']}/file")
    assert video.status_code == 200 and b"ftyp" in video.content[:64]
    assert (
        client.post(
            f"/api/v1/generations/{job_id}/review",
            json={
                "exact_words": True,
                "consistent_identity": True,
                "natural_reactions": True,
                "lip_sync": True,
            },
        ).status_code
        == 409
    )


def test_gpu_not_faked_and_revocation(client):
    script, scene = setup_project(client)
    response = client.post(
        "/api/v1/generations",
        json={
            "conversation_id": script["id"],
            "scene_id": scene["id"],
            "kind": "animated",
        },
    )
    assert response.status_code in {422, 503}
    asset_id = scene["image_asset_id"]
    assert client.post(f"/api/v1/assets/{asset_id}/revoke").status_code == 200
    assert client.get(f"/api/v1/assets/{asset_id}/file").status_code == 404
    assert (
        client.post(
            "/api/v1/generations",
            json={"conversation_id": script["id"], "scene_id": scene["id"], "kind": "storyboard"},
        ).status_code
        == 404
    )


def test_audio_alignment_and_duration(tmp_path):
    clips = []
    for i in range(2):
        path = tmp_path / f"{i}.wav"
        wav_write(path, array("h", [1000]) * RATE * 4)
        clips.append(path)
    turns = [
        {"character_id": "a", "text": "first", "pause_after": 1},
        {"character_id": "b", "text": "second", "pause_after": 1},
    ]
    paths, timeline, duration = AudioService().align(
        turns, clips, ["a", "b"], tmp_path, 10
    )
    assert duration == 9 and timeline[1]["start"] == 5 and len(paths) == 2
    from app.shared.audio_service import wav_read

    assert max(wav_read(paths[1])[: RATE * 5]) == 0
    _, _, duration = AudioService().align(turns, clips, ["a", "b"], tmp_path, 60)
    assert duration == 9
    with pytest.raises(ValueError, match="Words were not changed"):
        AudioService().align(turns, clips, ["a", "b"], tmp_path, 8)


def test_generation_defaults_and_maximum(client):
    from app.generations.generation_schema import GenerationCreate
    from pydantic import ValidationError

    assert GenerationCreate(conversation_id="c", scene_id="s").kind == "animated"
    for seconds in (0, 61, 65):
        with pytest.raises(ValidationError):
            GenerationCreate(conversation_id="c", scene_id="s", target_seconds=seconds)


def test_audio_limit_and_silent_provider(tmp_path):
    from app.shared.audio_service import wav_read

    clip = tmp_path / "voice.wav"
    turns = [{"character_id": "a", "text": "hello", "pause_after": 5}]
    wav_write(clip, array("h", [1000]) * RATE * 60)
    paths, _, duration = AudioService().align(turns, [clip], ["a", "b"], tmp_path, 60)
    assert duration == 60
    assert len(wav_read(paths[0])) == RATE * 60
    wav_write(clip, array("h", [1000]) * (RATE * 60 + 1))
    with pytest.raises(ValueError, match="maximum is 60s"):
        AudioService().align(turns, [clip], ["a", "b"], tmp_path, 65)
    wav_write(clip, array("h", [0]) * RATE)
    with pytest.raises(ValueError, match="silent audio"):
        AudioService().align(turns, [clip], ["a", "b"], tmp_path, 60)


def test_animated_worker_exports_short_video_with_audio(client, monkeypatch, tmp_path):
    """Stub model inference only; exercise real alignment, muxing and publication."""
    import math
    import subprocess
    import imageio_ffmpeg
    from app.config import settings
    from app.generations import generation_worker, generation_service
    from app.shared.audio_service import wav_read

    monkeypatch.setattr(settings, "enable_animated_renders", True)
    monkeypatch.setattr(settings, "speech_provider", "kokoro")
    monkeypatch.setattr(settings, "video_provider", "sadtalker")
    monkeypatch.setattr(settings, "speech_url", "http://test-model")
    monkeypatch.setattr(settings, "video_url", "http://test-model")
    monkeypatch.setattr(generation_service, "lightweight_ready", lambda: True)

    class Speech:
        def synthesize(self, text, voice, output, profile):
            wav_write(output, array("h", (int(4000 * math.sin(2 * math.pi * 440 * i / RATE)) for i in range(RATE))))
            return output

    class Video:
        def generate(self, image, tracks, output, prompt):
            duration = len(wav_read(tracks[0])) / RATE
            assert duration == pytest.approx(2.4)
            assert len(wav_read(tracks[1])) == len(wav_read(tracks[0]))
            subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-f", "lavfi", "-i",
                            "testsrc2=size=128x128:rate=25", "-t", str(duration),
                            "-c:v", "libx264", str(output)], check=True, capture_output=True)
            return output

    monkeypatch.setattr(generation_worker, "speech_provider", lambda _: Speech())
    monkeypatch.setattr(generation_worker, "video_provider", lambda _: Video())
    script, scene = setup_project(client)
    response = client.post("/api/v1/generations", json={"conversation_id": script["id"], "scene_id": scene["id"]})
    assert response.status_code == 201, response.text
    job_id = response.json()["id"]
    assert claim_job() == job_id
    run_generation(job_id)
    job = client.get(f"/api/v1/generations/{job_id}").json()
    assert job["status"] == "completed", job
    assert job["duration"] == pytest.approx(2.4)
    output = tmp_path / "output.mp4"
    download = client.get(f"/api/v1/assets/{job['output_asset_id']}/file")
    assert download.status_code == 200, download.text
    output.write_bytes(download.content)
    decoded = tmp_path / "decoded.wav"
    AudioService().normalize(output, decoded)
    samples = wav_read(decoded)
    assert max(samples) > 1000
    assert len(samples) / RATE == pytest.approx(2.4, abs=0.1)
    result = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-i", str(output), "-map", "0:v:0", "-f", "null", "-"], capture_output=True)
    assert result.returncode == 0
