from sqlalchemy import JSON, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.shared.base_model import Record


class Conversation(Record):
    __tablename__ = "conversations"
    title: Mapped[str] = mapped_column(String(200))
    mode: Mapped[str] = mapped_column(String(20), default="scripted")
    turns: Mapped[list] = mapped_column(JSON, default=list)
    approved: Mapped[bool] = mapped_column(Boolean, default=False)
