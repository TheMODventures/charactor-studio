from fastapi import HTTPException
from app.config import settings
from app.shared.storage_service import StorageService


class CharacterService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, data, character_id=None):
        if settings.fixed_demo_mode:
            raise HTTPException(
                403,
                "Character creation and editing are disabled for this fixed-cast MVP",
            )
        storage = StorageService(self.repository.session)
        for field, kind in [("image_asset_id", "image"), ("voice_asset_id", "voice")]:
            if value := getattr(data, field):
                storage.get(value, kind)
        values = data.model_dump()
        if character_id:
            return self.repository.update(self.repository.get(character_id), values)
        return self.repository.create(values)
