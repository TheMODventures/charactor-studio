from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_session
from app.conversations.conversation_repository import ConversationRepository
from app.conversations.conversation_service import ConversationService
from app.conversations.conversation_schema import ConversationCreate, ConversationRead
from app.conversations.conversation_schema import DraftRequest
from app.characters.character_repository import CharacterRepository
from app.ai.qwen_provider import QwenProvider

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.get("", response_model=list[ConversationRead])
def list_records(db: Session = Depends(get_session)):
    return ConversationRepository(db).list()


@router.post("", response_model=ConversationRead, status_code=201)
def create(data: ConversationCreate, db: Session = Depends(get_session)):
    return ConversationService(ConversationRepository(db)).save(data)


@router.post("/draft")
def draft(data: DraftRequest, db: Session = Depends(get_session)):
    characters = [CharacterRepository(db).get(i) for i in data.character_ids]
    if len(set(data.character_ids)) != 2 or any(c.archived for c in characters):
        raise HTTPException(422, "Choose two distinct active characters")
    profiles = [{"id": c.id, "name": c.name, "profile": c.profile} for c in characters]
    return {"turns": QwenProvider().generate(data.topic, profiles), "approved": False}


@router.get("/{record_id}", response_model=ConversationRead)
def get(record_id: str, db: Session = Depends(get_session)):
    return ConversationRepository(db).get(record_id)


@router.put("/{record_id}", response_model=ConversationRead)
def update(
    record_id: str, data: ConversationCreate, db: Session = Depends(get_session)
):
    return ConversationService(ConversationRepository(db)).save(data, record_id)
