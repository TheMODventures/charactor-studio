import time
import httpx
from app.config import settings

_cached_at = 0.0
_cached_ready = False


def lightweight_ready():
    """Short readiness cache; configuration alone must not enable rendering."""
    global _cached_at, _cached_ready
    if time.monotonic() - _cached_at < 10:
        return _cached_ready
    _cached_ready = False
    try:
        for url in {settings.speech_url, settings.video_url}:
            if not url:
                return False
            response = httpx.get(
                url.rstrip("/") + "/health",
                headers={"Authorization": f"Bearer {settings.provider_token}"},
                timeout=5,
            )
            response.raise_for_status()
            if response.json().get("model") != "kokoro+sadtalker":
                return False
        _cached_ready = True
    except (httpx.HTTPError, ValueError):
        pass
    finally:
        _cached_at = time.monotonic()
    return _cached_ready
