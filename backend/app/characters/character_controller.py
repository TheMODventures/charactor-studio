from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_session
from app.characters.character_repository import CharacterRepository
from app.characters.character_service import CharacterService
from app.characters.character_schema import CharacterCreate, CharacterRead

router = APIRouter(prefix="/characters", tags=["characters"])


@router.get("", response_model=list[CharacterRead])
def list_records(db: Session = Depends(get_session)):
    return CharacterRepository(db).list()


@router.post("", response_model=CharacterRead, status_code=201)
def create(data: CharacterCreate, db: Session = Depends(get_session)):
    return CharacterService(CharacterRepository(db)).save(data)


@router.get("/{record_id}", response_model=CharacterRead)
def get(record_id: str, db: Session = Depends(get_session)):
    return CharacterRepository(db).get(record_id)


@router.put("/{record_id}", response_model=CharacterRead)
def update(record_id: str, data: CharacterCreate, db: Session = Depends(get_session)):
    return CharacterService(CharacterRepository(db)).save(data, record_id)
