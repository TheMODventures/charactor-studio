from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.database import get_session
from app.generations.generation_model import Generation
from app.generations.generation_repository import GenerationRepository
from app.generations.generation_service import GenerationService
from app.generations.generation_schema import (
    GenerationCreate,
    GenerationRead,
    ReviewRequest,
)

router = APIRouter(prefix="/generations", tags=["generations"])


@router.get("", response_model=list[GenerationRead])
def list_jobs(db: Session = Depends(get_session)):
    return GenerationRepository(db).list()


@router.post("", status_code=201, response_model=GenerationRead)
def create(data: GenerationCreate, db: Session = Depends(get_session)):
    return GenerationService(GenerationRepository(db)).create(data)


@router.get("/{job_id}", response_model=GenerationRead)
def get(job_id: str, db: Session = Depends(get_session)):
    return GenerationRepository(db).get(job_id)


@router.post("/{job_id}/retry", status_code=201, response_model=GenerationRead)
def retry(job_id: str, db: Session = Depends(get_session)):
    repo = GenerationRepository(db)
    return GenerationService(repo).retry(repo.get(job_id))


@router.post("/{job_id}/cancel")
def cancel(job_id: str, db: Session = Depends(get_session)):
    GenerationRepository(db).get(job_id)
    result = db.execute(
        update(Generation)
        .where(Generation.id == job_id, Generation.status == "queued")
        .values(status="cancelled", stage="Cancelled")
    )
    db.commit()
    if not result.rowcount:
        raise HTTPException(
            409, "Only queued jobs can be cancelled; running GPU calls must finish"
        )
    return {"status": "cancelled"}


@router.post("/{job_id}/review", response_model=GenerationRead)
def review(job_id: str, data: ReviewRequest, db: Session = Depends(get_session)):
    repo = GenerationRepository(db)
    job = repo.get(job_id)
    if job.status != "completed" or job.settings["kind"] != "animated":
        raise HTTPException(
            409, "Only a completed animated render can receive final review"
        )
    return repo.update(job, {"review": data.model_dump()})


@router.get("/{job_id}/manifest")
def manifest(job_id: str, db: Session = Depends(get_session)):
    job = GenerationRepository(db).get(job_id)
    return {
        "id": job.id,
        "status": job.status,
        "inputs": job.settings,
        "review": job.review,
        "duration": job.duration,
        "disclosure": "AI-generated fictional characters",
    }
