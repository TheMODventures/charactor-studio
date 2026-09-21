from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class DialogueTurn(BaseModel):
    character_id: str
    text: str = Field(min_length=1, max_length=1500)
    direction: str = Field(default="", max_length=500)
    pause_after: float = Field(default=0.4, ge=0, le=5)


class ConversationCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    mode: Literal["scripted", "generated"] = "scripted"
    turns: list[DialogueTurn] = Field(min_length=1, max_length=40)
    approved: bool = False


class ConversationRead(ConversationCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    version: int


class DraftRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=2000)
    character_ids: list[str] = Field(min_length=2, max_length=2)
