import json
import httpx
from fastapi import HTTPException
from pydantic import ValidationError
from app.config import settings
from app.conversations.conversation_schema import DialogueTurn


class QwenProvider:
    def generate(self, prompt: str, profiles: list[dict]) -> list[dict]:
        system = (
            "Write an original approximately 120-word conversation. Return JSON {turns: [{character_id, text, direction, pause_after}]}. Use exactly the supplied character IDs and both characters. Honor each profile. Do not infer dialect from race. No impersonation. Profiles: "
            + json.dumps(profiles)
        )
        try:
            response = httpx.post(
                settings.ollama_url.rstrip("/") + "/api/chat",
                json={
                    "model": settings.dialogue_model,
                    "stream": False,
                    "format": "json",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": prompt},
                    ],
                },
                timeout=120,
            )
            response.raise_for_status()
            turns = json.loads(response.json()["message"]["content"])["turns"]
            if not 2 <= len(turns) <= 40:
                raise ValueError("Invalid turn count")
            result = [DialogueTurn.model_validate(t).model_dump() for t in turns]
            if {t["character_id"] for t in result} != {p["id"] for p in profiles}:
                raise ValueError("Invalid speaker IDs")
            return result
        except (httpx.HTTPError, KeyError, ValueError, ValidationError) as exc:
            raise HTTPException(
                503,
                "Dialogue provider unavailable or returned an invalid draft. Start Ollama, install the configured Qwen model, or use creator-written dialogue.",
            ) from exc
