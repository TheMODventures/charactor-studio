from pathlib import Path
import shutil
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
    if not settings.seed_characters and not settings.fixed_demo_mode:
        return
    with Session(get_engine()) as db:
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
            existing = db.get(Character, identity)
            preset = "af_heart" if identity == "royale" else "af_bella"
            if existing:
                if "voice_preset" not in existing.profile:
                    existing.profile = {**existing.profile, "voice_preset": preset}
                continue
            profile = CharacterProfile(
                personality=personality,
                expressiveness=expression,
                gestures=gestures,
                voice_preset=preset,
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
        if demo.exists() and not db.get(Asset, "demo-scene-image"):
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

        if settings.fixed_demo_mode:
            if not demo.is_file():
                raise RuntimeError("The bundled MVP scene image is missing")
            target = settings.assets_dir / "scenes" / "mvp-original.png"
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                shutil.copyfile(demo, target)
            if not db.get(Asset, "mvp-scene-image"):
                db.add(
                    Asset(
                        id="mvp-scene-image",
                        kind="image",
                        path="scenes/mvp-original.png",
                        original_name="R.Royale and Summer Breeze.png",
                        rights="original",
                        rights_note="AI-generated fictional scene selected by the creator for this fixed-image MVP",
                    )
                )
            if not db.get(Scene, "mvp-scene"):
                db.add(
                    Scene(
                        id="mvp-scene",
                        name="The living room",
                        image_asset_id="mvp-scene-image",
                        character_ids=["royale", "summer"],
                        prompt="Two women seated together in a warm living room. R.Royale on the left, Summer Breeze on the right. Natural eye contact, subtle gestures and attentive listening while the other speaks.",
                        approved=True,
                    )
                )
            db.commit()
