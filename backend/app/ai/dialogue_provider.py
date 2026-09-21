from typing import Protocol


class DialogueProvider(Protocol):
    def generate(self, prompt: str, profiles: list[dict]) -> list[dict[str, str]]:
        """Return dialogue turns containing character_id and text."""
        ...
