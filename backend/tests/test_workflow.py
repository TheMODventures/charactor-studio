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
        },
    )
    assert response.status_code == 201
    job_id = response.json()["id"]
    assert claim_job() == job_id
    assert claim_job() is None
    run_generation(job_id)
    job = client.get(f"/api/v1/generations/{job_id}").json()
    assert job["status"] == "completed", job
    assert job["duration"] == 10
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
            json={"conversation_id": script["id"], "scene_id": scene["id"]},
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
    assert duration == 10 and timeline[1]["start"] == 5 and len(paths) == 2
    from app.shared.audio_service import wav_read

    assert max(wav_read(paths[1])[: RATE * 5]) == 0
    with pytest.raises(ValueError, match="Words were not changed"):
        AudioService().align(turns, clips, ["a", "b"], tmp_path, 60)
