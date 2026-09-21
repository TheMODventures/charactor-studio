from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Record


class Asset(Record):
    __tablename__ = "assets"
    kind: Mapped[str] = mapped_column(String(30))
    path: Mapped[str] = mapped_column(String(500))
    original_name: Mapped[str] = mapped_column(String(300))
    rights: Mapped[str] = mapped_column(String(30))
    rights_note: Mapped[str] = mapped_column(String(2000))
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
