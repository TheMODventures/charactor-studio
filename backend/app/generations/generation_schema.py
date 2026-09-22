from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class GenerationCreate(BaseModel):
    conversation_id: str
    scene_id: str
    kind: Literal["storyboard", "animated"] = "animated"
    target_seconds: int = Field(default=60, ge=1, le=60)


class GenerationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    version: int
    conversation_id: str
    scene_id: str
    status: str
    stage: str
    progress: int
    settings: dict
    error: str | None
    output_asset_id: str | None
    duration: float | None
    review: dict


class ReviewRequest(BaseModel):
    exact_words: bool
    consistent_identity: bool
    natural_reactions: bool
    lip_sync: bool
    notes: str = Field(default="", max_length=2000)
