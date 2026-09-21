from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_session
from app.scenes.scene_repository import SceneRepository
from app.scenes.scene_service import SceneService
from app.scenes.scene_schema import SceneCreate, SceneRead

router = APIRouter(prefix="/scenes", tags=["scenes"])


@router.get("", response_model=list[SceneRead])
def list_records(db: Session = Depends(get_session)):
    return SceneRepository(db).list()


@router.post("", response_model=SceneRead, status_code=201)
def create(data: SceneCreate, db: Session = Depends(get_session)):
    return SceneService(SceneRepository(db)).save(data)


@router.get("/{record_id}", response_model=SceneRead)
def get(record_id: str, db: Session = Depends(get_session)):
    return SceneRepository(db).get(record_id)


@router.put("/{record_id}", response_model=SceneRead)
def update(record_id: str, data: SceneCreate, db: Session = Depends(get_session)):
    return SceneService(SceneRepository(db)).save(data, record_id)
