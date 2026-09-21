from sqlalchemy import JSON, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Record


class Character(Record):
    __tablename__ = "characters"
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String(2000), default="")
    color: Mapped[str] = mapped_column(String(20), default="#a599e9")
    profile: Mapped[dict] = mapped_column(JSON, default=dict)
    image_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    voice_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
