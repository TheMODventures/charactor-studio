from pathlib import Path
import httpx
from app.config import settings


class KokoroProvider:
    def synthesize(
        self,
        text: str,
        voice_reference: Path | None,
        output_path: Path,
        profile: dict | None = None,
    ) -> Path:
        response = httpx.post(
            settings.speech_url.rstrip("/") + "/synthesize",
            data={
                "text": text,
                "voice": (profile or {}).get("voice_preset", "af_heart"),
            },
            headers={"Authorization": f"Bearer {settings.provider_token}"},
            timeout=settings.provider_timeout,
        )
        response.raise_for_status()
        if len(response.content) > 50_000_000:
            raise RuntimeError("Speech response exceeds size limit")
        output_path.write_bytes(response.content)
        return output_path
