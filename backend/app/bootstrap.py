from pathlib import Path
import shutil
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import Base, get_engine
from app.config import settings
from app.characters.character_model import Character
from app.assets.asset_model import Asset  # noqa: F401
from app.conversations.conversation_model import Conversation  # noqa: F401
from app.scenes.scene_model import Scene  # noqa: F401
from app.generations.generation_model import Generation  # noqa: F401
from app.characters.character_schema import CharacterProfile


def initialize():
    settings.assets_dir.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(get_engine())
    if not settings.seed_characters:
        return
    with Session(get_engine()) as db:
        if db.scalar(select(Character.id).limit(1)):
            return
        profiles = [
            (
                "royale",
                "R.Royale",
                "Calm presence. A dry sense of humor.",
                "#b9ace8",
                "Calm, dry humor, thoughtful and controlled. An original fictional African-American woman.",
                0.3,
                "Small hand movements; attentive eye contact",
            ),
            (
                "summer",
                "Summer Breeze",
                "Big energy. A little sunshine.",
                "#eac391",
                "Warm, animated, expressive and outgoing. An original fictional African-American woman.",
                0.75,
                "Expressive hands; warm smiles; lively but natural reactions",
            ),
        ]
        for (
            identity,
            name,
            description,
            color,
            personality,
            expression,
            gestures,
        ) in profiles:
            profile = CharacterProfile(
                personality=personality, expressiveness=expression, gestures=gestures
            ).model_dump()
            db.add(
                Character(
                    id=identity,
                    name=name,
                    description=description,
                    color=color,
                    profile=profile,
                )
            )
        db.commit()

        demo = Path(__file__).resolve().parents[1] / "demo_assets" / "scene.png"
        if demo.exists():
            target = settings.assets_dir / "scenes" / "original-demo.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(demo, target)
            asset = Asset(
                id="demo-scene-image",
                kind="image",
                path="scenes/original-demo.png",
                original_name="Original fictional scene.png",
                rights="original",
                rights_note="AI-generated fictional reference created for this prototype; creator approval pending",
            )
            db.add(asset)
            db.add(
                Scene(
                    id="demo-scene",
                    name="The living room",
                    image_asset_id=asset.id,
                    character_ids=["royale", "summer"],
                    prompt="Two women seated together in a warm living room. R.Royale on the left, Summer Breeze on the right. Natural eye contact, subtle gestures and attentive listening while the other speaks.",
                    approved=False,
                )
            )
            db.commit()
