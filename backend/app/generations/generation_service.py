from fastapi import HTTPException
from app.characters.character_repository import CharacterRepository
from app.characters.character_schema import CharacterRead
from app.conversations.conversation_repository import ConversationRepository
from app.conversations.conversation_schema import ConversationRead
from app.scenes.scene_repository import SceneRepository
from app.scenes.scene_schema import SceneRead
from app.shared.storage_service import StorageService
from app.config import settings


class GenerationService:
    def __init__(self, repository):
        self.repository = repository

    def create(self, data):
        self.check_feature(data.kind)
        db = self.repository.session
        conversation = ConversationRepository(db).get(data.conversation_id)
        scene = SceneRepository(db).get(data.scene_id)
        if not conversation.approved or not scene.approved:
            raise HTTPException(
                422, "Approve the dialogue and shared scene before rendering"
            )
        speakers = {t["character_id"] for t in conversation.turns}
        if speakers != set(scene.character_ids):
            raise HTTPException(
                422, "The dialogue must use both scene characters and no other speakers"
            )
        storage = StorageService(db)
        storage.get(scene.image_asset_id, "image")
        characters = [CharacterRepository(db).get(i) for i in scene.character_ids]
        for c in characters:
            if c.archived:
                raise HTTPException(422, "Restore archived characters before rendering")
            if data.kind == "animated":
                if not c.voice_asset_id:
                    raise HTTPException(
                        422, f"Add an authorized voice reference for {c.name}"
                    )
                storage.get(c.voice_asset_id, "voice")
        if data.kind == "animated" and (
            not settings.speech_url or not settings.video_url
        ):
            raise HTTPException(
                503,
                "GPU services are not configured. Connect Chatterbox and InfiniteTalk in deployment settings. A storyboard is available without GPU services.",
            )
        if data.kind == "animated" and len({c.voice_asset_id for c in characters}) != 2:
            raise HTTPException(422, "Choose two distinct voice references")
        snapshot = {
            "kind": data.kind,
            "target_seconds": data.target_seconds,
            "conversation": ConversationRead.model_validate(conversation).model_dump(
                mode="json"
            ),
            "scene": SceneRead.model_validate(scene).model_dump(mode="json"),
            "characters": [
                CharacterRead.model_validate(c).model_dump(mode="json")
                for c in characters
            ],
            "providers": {
                "speech": "chatterbox",
                "video": "infinitetalk",
                "dialogue": settings.dialogue_model,
            },
        }
        return self.repository.create(
            {
                "conversation_id": conversation.id,
                "scene_id": scene.id,
                "settings": snapshot,
            }
        )

    @staticmethod
    def check_feature(kind):
        if kind == "animated" and not settings.enable_animated_renders:
            raise HTTPException(
                503,
                "Animated speech and lip-sync are not functional at the moment for this MVP",
            )

    def retry(self, job):
        self.check_feature(job.settings["kind"])
        if job.status not in {"failed", "cancelled"}:
            raise HTTPException(409, "Only failed or cancelled jobs can be retried")
        # Preserve the original versioned inputs, even after character edits.
        return self.repository.create(
            {
                "conversation_id": job.conversation_id,
                "scene_id": job.scene_id,
                "settings": job.settings,
            }
        )
