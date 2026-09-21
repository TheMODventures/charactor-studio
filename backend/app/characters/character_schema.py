from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CharacterProfile(BaseModel):
    personality: str = Field(default="", max_length=2000)
    region: str = Field(default="Creator defined", max_length=200)
    vocabulary: str = Field(default="", max_length=2000)
    aave: str = Field(default="Creator defined; no automatic dialect", max_length=1000)
    slang: int = Field(default=0, ge=0, le=100)
    pronunciation: str = Field(default="", max_length=2000)
    cadence: str = Field(default="Natural", max_length=300)
    code_switching: str = Field(default="Context dependent", max_length=1000)
    expressiveness: float = Field(default=0.5, ge=0, le=1)
    pace: float = Field(default=1, ge=0.8, le=1.2)
    gestures: str = Field(default="Subtle conversational gestures", max_length=1000)
    voice_notes: str = Field(default="", max_length=1000)
    voice_preset: str = Field(default="af_heart", pattern=r"^af_[a-z]+$")


class CharacterCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)
    color: str = Field(default="#a599e9", pattern=r"^#[0-9a-fA-F]{6}$")
    profile: CharacterProfile = Field(default_factory=CharacterProfile)
    image_asset_id: str | None = None
    voice_asset_id: str | None = None
    archived: bool = False


class CharacterRead(CharacterCreate):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    version: int
