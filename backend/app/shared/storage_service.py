from io import BytesIO
from pathlib import Path
from uuid import uuid4
import wave
from fastapi import HTTPException
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session
from app.assets.asset_model import Asset
from app.config import settings


class StorageService:
    def __init__(self, session: Session):
        self.session = session

    def get(self, asset_id: str, kind: str | None = None) -> Asset:
        asset = self.session.get(Asset, asset_id)
        if not asset or asset.revoked:
            raise HTTPException(404, "Asset missing or authorization revoked")
        if kind and asset.kind != kind:
            raise HTTPException(422, f"Expected {kind} asset")
        return asset

    def path(self, asset: Asset) -> Path:
        root = settings.assets_dir.resolve()
        path = (root / asset.path).resolve()
        if not path.is_relative_to(root):
            raise HTTPException(400, "Invalid asset path")
        return path

    def register(
        self,
        path: Path,
        kind: str,
        name: str,
        rights="generated",
        note="Created in Character Studio",
    ):
        asset = Asset(
            kind=kind,
            path=str(path.resolve().relative_to(settings.assets_dir.resolve())),
            original_name=name,
            rights=rights,
            rights_note=note,
        )
        self.session.add(asset)
        self.session.commit()
        self.session.refresh(asset)
        return asset

    def upload(self, data: bytes, name: str, kind: str, rights: str, note: str):
        if settings.fixed_demo_mode and kind == "image":
            raise HTTPException(
                403, "Image uploads are disabled; this MVP uses the built-in image"
            )
        if kind not in {"image", "voice"} or rights not in {
            "original",
            "licensed",
            "authorized",
        }:
            raise HTTPException(422, "Invalid asset or rights type")
        if len(note.strip()) < 5 or len(note) > 2000:
            raise HTTPException(
                422, "Provide the ownership, license or authorization details"
            )
        if kind == "image" and rights == "authorized":
            raise HTTPException(
                422,
                "Real-person likeness uploads are not enabled; use original fictional or licensed fictional images",
            )
        try:
            if kind == "image":
                with Image.open(BytesIO(data)) as image:
                    if image.width * image.height > 20_000_000:
                        raise ValueError("Image exceeds 20 megapixels")
                    image.load()
                    result = BytesIO()
                    image.convert("RGB").save(result, format="JPEG")
                    data = result.getvalue()
                suffix = ".jpg"
            else:
                with wave.open(BytesIO(data)) as audio:
                    duration = audio.getnframes() / audio.getframerate()
                    if not 3 <= duration <= 30 or audio.getsampwidth() != 2:
                        raise ValueError(
                            "Use a 3–30 second, 16-bit PCM WAV voice recording"
                        )
                suffix = ".wav"
        except (
            UnidentifiedImageError,
            Image.DecompressionBombError,
            OSError,
            EOFError,
            wave.Error,
            ValueError,
        ) as exc:
            raise HTTPException(422, str(exc) or "Invalid media file") from exc
        folder = settings.assets_dir / ("characters" if kind == "image" else "audio")
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / (str(uuid4()) + suffix)
        path.write_bytes(data)
        return self.register(path, kind, Path(name).name[:300], rights, note)
