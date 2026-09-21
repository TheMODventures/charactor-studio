import json
from datetime import datetime, timezone
import httpx
from fastapi import APIRouter
from app.config import settings

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status")
def status():
    heartbeat = settings.assets_dir.parent / "worker-heartbeat.json"
    worker = False
    if heartbeat.exists():
        try:
            timestamp = datetime.fromisoformat(
                json.loads(heartbeat.read_text())["updated_at"]
            )
            worker = (datetime.now(timezone.utc) - timestamp).total_seconds() < 30
        except (ValueError, KeyError, OSError):
            pass
    return {
        "worker": worker,
        "providers": {
            "dialogue": {
                "name": settings.dialogue_model,
                "configured": bool(settings.ollama_url),
            },
            "speech": {"name": "Chatterbox", "configured": bool(settings.speech_url)},
            "video": {"name": "InfiniteTalk", "configured": bool(settings.video_url)},
        },
        "capabilities": {
            "scripted_dialogue": True,
            "storyboard": True,
            "ai_dialogue": bool(settings.enable_ai_drafts and settings.ollama_url),
            "animated_video": bool(
                settings.enable_animated_renders
                and settings.speech_url
                and settings.video_url
            ),
        },
        "limitations": [
            "Speech styles are preferences, not guaranteed dialect controls.",
            "Review exact words, faces, lip-sync and listening reactions after GPU generation.",
            "Uploaded likenesses must depict fictional characters; third-party real-person likeness verification is not enabled.",
        ],
    }


@router.post("/check")
def check():
    results = {}
    for name, url in [
        ("dialogue", settings.ollama_url),
        ("speech", settings.speech_url),
        ("video", settings.video_url),
    ]:
        if not url:
            results[name] = {"ready": False, "message": "Not configured"}
            continue
        try:
            suffix = "/api/tags" if name == "dialogue" else "/health"
            response = httpx.get(
                url.rstrip("/") + suffix,
                headers={"Authorization": f"Bearer {settings.provider_token}"},
                timeout=5,
            )
            response.raise_for_status()
            ready = True
            if name == "dialogue":
                ready = settings.dialogue_model in {
                    m["name"] for m in response.json().get("models", [])
                }
            results[name] = {
                "ready": ready,
                "message": "Connected"
                if ready
                else "Configured model is not installed",
            }
        except (httpx.HTTPError, ValueError, KeyError):
            results[name] = {"ready": False, "message": "Service not reachable"}
    return results
