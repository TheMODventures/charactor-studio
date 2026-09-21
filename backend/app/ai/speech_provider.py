from pathlib import Path
from typing import Protocol


class SpeechProvider(Protocol):
    def synthesize(self, text: str, voice_reference: Path, output_path: Path) -> Path:
        """Generate speech using an authorized voice reference."""
        ...
