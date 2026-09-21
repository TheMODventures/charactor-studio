from sqlalchemy import JSON, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Record


class Scene(Record):
    __tablename__ = "scenes"
    name: Mapped[str] = mapped_column(String(120))
    image_asset_id: Mapped[str] = mapped_column(String(36))
    character_ids: Mapped[list] = mapped_column(JSON)
    prompt: Mapped[str] = mapped_column(String(4000), default="")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
