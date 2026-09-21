from pathlib import Path
from contextlib import ExitStack
import httpx
from app.config import settings


class VideoHttpProvider:
    def generate(
        self,
        scene_image: Path,
        audio_tracks: list[Path],
        output_path: Path,
        prompt: str = "",
    ) -> Path:
        if not settings.video_url:
            raise RuntimeError(
                "Configure VIDEO_URL and start the selected video model service"
            )
        with ExitStack() as stack:
            files = {
                "image": (
                    scene_image.name,
                    stack.enter_context(scene_image.open("rb")),
                    "image/png"
                    if scene_image.suffix.lower() == ".png"
                    else "image/jpeg",
                )
            }
            for index, path in enumerate(audio_tracks):
                files[f"audio{index + 1}"] = (
                    path.name,
                    stack.enter_context(path.open("rb")),
                    "audio/wav",
                )
            with httpx.stream(
                "POST",
                settings.video_url.rstrip("/") + "/generate",
                files=files,
                data={"prompt": prompt},
                headers={"Authorization": f"Bearer {settings.provider_token}"},
                timeout=settings.provider_timeout,
            ) as response:
                response.raise_for_status()
                with output_path.open("wb") as output:
                    size = 0
                    for chunk in response.iter_bytes():
                        size += len(chunk)
                        if size > 500_000_000:
                            raise RuntimeError("Video response exceeds size limit")
                        output.write(chunk)
        return output_path
