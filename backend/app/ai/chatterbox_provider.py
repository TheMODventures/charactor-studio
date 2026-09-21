from pathlib import Path
import httpx
from app.config import settings


class ChatterboxProvider:
    def synthesize(
        self,
        text: str,
        voice_reference: Path,
        output_path: Path,
        profile: dict | None = None,
    ) -> Path:
        if not settings.speech_url:
            raise RuntimeError(
                "Configure SPEECH_URL and start the Chatterbox model service"
            )
        with voice_reference.open("rb") as voice:
            response = httpx.post(
                settings.speech_url.rstrip("/") + "/synthesize",
                files={"reference": ("voice.wav", voice, "audio/wav")},
                data={
                    "text": text,
                    "expressiveness": str((profile or {}).get("expressiveness", 0.5)),
                },
                headers={"Authorization": f"Bearer {settings.provider_token}"},
                timeout=settings.provider_timeout,
            )
        response.raise_for_status()
        if len(response.content) > 50_000_000:
            raise RuntimeError("Speech response exceeds size limit")
        output_path.write_bytes(response.content)
        return output_path
