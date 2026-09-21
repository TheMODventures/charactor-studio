from sqlalchemy import JSON, String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Record


class Generation(Record):
    __tablename__ = "generations"
    status: Mapped[str] = mapped_column(String(32), default="queued")
    stage: Mapped[str] = mapped_column(String(100), default="Waiting for worker")
    progress: Mapped[int] = mapped_column(Integer, default=0)
    conversation_id: Mapped[str] = mapped_column(String(36))
    scene_id: Mapped[str] = mapped_column(String(36))
    settings: Mapped[dict] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    output_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    duration: Mapped[float | None] = mapped_column(Float, nullable=True)
    review: Mapped[dict] = mapped_column(JSON, default=dict)
