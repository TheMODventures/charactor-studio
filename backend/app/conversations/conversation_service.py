from fastapi import HTTPException
from app.characters.character_repository import CharacterRepository


class ConversationService:
    def __init__(self, repository):
        self.repository = repository

    def save(self, data, conversation_id=None):
        characters = CharacterRepository(self.repository.session)
        for turn in data.turns:
            if characters.get(turn.character_id).archived:
                raise HTTPException(422, "An archived character cannot be used")
        values = data.model_dump()
        if conversation_id:
            return self.repository.update(self.repository.get(conversation_id), values)
        return self.repository.create(values)
