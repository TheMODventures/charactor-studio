from app.config import settings
from fastapi import HTTPException
from app.characters.character_repository import CharacterRepository
from app.shared.storage_service import StorageService


class SceneService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, data, scene_id=None):
        if settings.fixed_demo_mode:
            raise HTTPException(
                403, "This MVP uses the built-in scene; scene editing is disabled"
            )
        if len(set(data.character_ids)) != 2:
            raise HTTPException(
                422, "Choose two different characters, in left-to-right image order"
            )
        for character_id in data.character_ids:
            if CharacterRepository(self.repository.session).get(character_id).archived:
                raise HTTPException(422, "An archived character cannot be used")
        StorageService(self.repository.session).get(data.image_asset_id, "image")
        values = data.model_dump()
        if scene_id:
            return self.repository.update(self.repository.get(scene_id), values)
        return self.repository.create(values)
