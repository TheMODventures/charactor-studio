from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class SceneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    image_asset_id: str
    character_ids: list[str] = Field(min_length=2, max_length=2)
    prompt: str = Field(
        default="Two women in one scene, natural conversation and attentive listening.",
        max_length=4000,
    )
    approved: bool = False


class SceneRead(SceneCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    version: int
