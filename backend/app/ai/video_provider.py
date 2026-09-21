from pathlib import Path
from typing import Protocol


class VideoProvider(Protocol):
    def generate(
        self, scene_image: Path, audio_tracks: list[Path], output_path: Path
    ) -> Path:
        """Animate a shared scene using aligned, per-character audio tracks."""
        ...
