from app.shared.base_repository import Repository
from app.characters.character_model import Character


class CharacterRepository(Repository):
    model = Character
