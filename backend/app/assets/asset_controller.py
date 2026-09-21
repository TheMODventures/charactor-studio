from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_session
from app.shared.storage_service import StorageService
from app.assets.asset_model import Asset
from app.config import settings
from app.generations.generation_model import Generation

router = APIRouter(prefix="/assets", tags=["assets"])


def serialize(asset):
    return {
        "id": asset.id,
        "kind": asset.kind,
        "name": asset.original_name,
        "rights": asset.rights,
        "rights_note": asset.rights_note,
        "url": f"/api/v1/assets/{asset.id}/file",
        "revoked": asset.revoked,
    }


@router.get("")
def list_assets(db: Session = Depends(get_session)):
    return [
        serialize(a) for a in db.scalars(select(Asset).where(Asset.revoked.is_(False)))
    ]


@router.post("", status_code=201)
async def upload(
    file: UploadFile = File(...),
    kind: str = Form(...),
    rights: str = Form(...),
    rights_note: str = Form(...),
    consent: bool = Form(...),
    db: Session = Depends(get_session),
):
    if settings.fixed_demo_mode and kind == "image":
        raise HTTPException(403, "Image uploads are disabled for this MVP")
    if not consent:
        raise HTTPException(422, "Rights confirmation is required")
    data = await file.read(20 * 1024 * 1024 + 1)
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "Maximum upload is 20 MB")
    return serialize(
        StorageService(db).upload(
            data, file.filename or "asset", kind, rights, rights_note
        )
    )


@router.get("/{asset_id}/file")
def download(asset_id: str, db: Session = Depends(get_session)):
    storage = StorageService(db)
    asset = storage.get(asset_id)
    if asset.kind == "video":
        job = db.scalar(
            select(Generation).where(Generation.output_asset_id == asset.id)
        )
        if job:
            storage.get(job.settings["scene"]["image_asset_id"], "image")
            if job.settings["kind"] == "animated":
                for character in job.settings["characters"]:
                    storage.get(character["voice_asset_id"], "voice")
    path = storage.path(asset)
    if not path.is_file():
        raise HTTPException(404, "Asset file is unavailable")
    return FileResponse(
        path, filename=asset.original_name, content_disposition_type="inline"
    )


@router.post("/{asset_id}/revoke")
def revoke(asset_id: str, db: Session = Depends(get_session)):
    if settings.fixed_demo_mode and asset_id == "mvp-scene-image":
        raise HTTPException(403, "The built-in demo image cannot be removed")
    asset = StorageService(db).get(asset_id)
    asset.revoked = True
    db.commit()
    return {"revoked": True}
