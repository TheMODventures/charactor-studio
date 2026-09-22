import json
import logging
import time
import threading
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from app.database import get_engine
from app.config import settings
from app.generations.generation_model import Generation
from app.shared.storage_service import StorageService
from app.shared.audio_service import AudioService
from app.shared.video_service import VideoService
from app.ai.provider_factory import speech_provider, video_provider

logger = logging.getLogger(__name__)


def claim_job():
    with Session(get_engine()) as db:
        job_id = db.scalar(
            select(Generation.id)
            .where(Generation.status == "queued")
            .order_by(Generation.created_at)
            .limit(1)
        )
        if job_id:
            result = db.execute(
                update(Generation)
                .where(Generation.id == job_id, Generation.status == "queued")
                .values(status="running", stage="Preparing inputs", progress=5)
            )
            db.commit()
            if result.rowcount:
                return job_id
    return None


def run_generation(job_id: str):
    with Session(get_engine()) as db:
        job = db.get(Generation, job_id)
        if not job or job.status != "running":
            return

        def progress(stage, percent):
            job.stage = stage
            job.progress = percent
            db.commit()

        try:
            snapshot = job.settings
            if (
                settings.fixed_demo_mode
                and snapshot["scene"]["image_asset_id"] != "mvp-scene-image"
            ):
                raise ValueError("Only the built-in scene can be rendered in this MVP")
            if snapshot["kind"] == "animated" and not settings.enable_animated_renders:
                raise ValueError(
                    "Animated speech and lip-sync are not functional at the moment for this MVP"
                )
            storage = StorageService(db)
            scene = snapshot["scene"]
            image = storage.path(storage.get(scene["image_asset_id"], "image"))
            folder = settings.assets_dir / "outputs" / job.id
            folder.mkdir(parents=True, exist_ok=True)
            output = folder / "conversation.mp4"
            if snapshot["kind"] == "storyboard":
                progress("Rendering silent storyboard", 40)
                # A storyboard has no measured speech; use a reading-time estimate.
                turns = snapshot["conversation"]["turns"]
                duration = min(
                    60,
                    snapshot["target_seconds"],
                    max(1, sum(len(t["text"].split()) / 2.3 for t in turns)
                        + sum(t["pause_after"] for t in turns[:-1])),
                )
                VideoService().storyboard(image, output, duration)
            else:
                providers = snapshot["providers"]
                if (
                    providers["speech"] != settings.speech_provider
                    or providers["video"] != settings.video_provider
                ):
                    raise ValueError(
                        "Providers changed since this job was saved. Create a new render."
                    )
                speech = speech_provider(providers["speech"])
                video = video_provider(providers["video"])
                characters = {c["id"]: c for c in snapshot["characters"]}
                turns = snapshot["conversation"]["turns"]
                clips = []
                audio = AudioService()
                for index, turn in enumerate(turns):
                    c = characters[turn["character_id"]]
                    voice = (
                        storage.path(storage.get(c["voice_asset_id"], "voice"))
                        if providers["speech"] == "chatterbox"
                        else None
                    )
                    progress(
                        f"Generating voice {index + 1}/{len(turns)}",
                        10 + int(35 * index / len(turns)),
                    )
                    raw = speech.synthesize(
                        turn["text"], voice, folder / f"raw-{index}.wav", c["profile"]
                    )
                    clips.append(
                        audio.normalize(
                            raw,
                            folder / f"turn-{index}.wav",
                            c["profile"].get("pace", 1),
                        )
                    )
                progress("Aligning two speaker tracks", 50)
                tracks, timeline, duration = audio.align(
                    turns,
                    clips,
                    scene["character_ids"],
                    folder,
                    snapshot["target_seconds"],
                )
                (folder / "timeline.json").write_text(json.dumps(timeline, indent=2))
                progress(
                    "Animating both portraits"
                    if providers["video"] == "sadtalker"
                    else "Animating the shared scene",
                    65,
                )
                prompt = (
                    scene["prompt"]
                    + " Left-to-right character performance: "
                    + json.dumps(
                        [
                            {
                                "name": c["name"],
                                "gestures": c["profile"].get("gestures", ""),
                                "personality": c["profile"].get("personality", ""),
                            }
                            for c in snapshot["characters"]
                        ]
                    )
                )
                prompt += " Per-turn directions: " + json.dumps(
                    [
                        {
                            "character_id": t["character_id"],
                            "start": t["start"],
                            "end": t["end"],
                            "direction": t.get("direction", ""),
                        }
                        for t in timeline
                    ]
                )
                raw_video = video.generate(image, tracks, folder / "raw.mp4", prompt)
                progress("Mixing and exporting", 90)
                VideoService().finalize(raw_video, folder / "mix.wav", output)
            # Revocation during a long render prevents publishing its output.
            db.expire_all()
            storage.get(scene["image_asset_id"], "image")
            if (
                snapshot["kind"] == "animated"
                and snapshot["providers"]["speech"] == "chatterbox"
            ):
                for c in snapshot["characters"]:
                    storage.get(c["voice_asset_id"], "voice")
            job.duration = duration
            job.output_asset_id = storage.register(
                output, "video", f"{snapshot['kind']}-{job.id[:8]}.mp4"
            ).id
            job.status = "completed"
            job.stage = (
                "Ready for review"
                if snapshot["kind"] == "animated"
                else "Storyboard ready — no voice or animation"
            )
            job.progress = 100
            db.commit()
        except Exception as exc:
            logger.exception("Generation %s failed", job_id)
            db.rollback()
            job = db.get(Generation, job_id)
            job.status = "failed"
            job.stage = "Needs attention"
            job.error = (
                str(getattr(exc, "detail", str(exc)))[:1800]
                or "Generation failed; inspect worker logs"
            )
            db.commit()


def main():
    from app.bootstrap import initialize

    initialize()
    # The deployment runs one worker. Recover jobs interrupted by a process restart.
    with Session(get_engine()) as db:
        db.execute(
            update(Generation)
            .where(Generation.status == "running")
            .values(
                status="failed",
                stage="Worker restarted",
                error="Worker stopped during rendering. Retry this job.",
            )
        )
        db.commit()
    heartbeat = settings.assets_dir.parent / "worker-heartbeat.json"

    def report_heartbeat():
        while True:
            heartbeat.parent.mkdir(parents=True, exist_ok=True)
            heartbeat.write_text(
                json.dumps({"updated_at": datetime.now(timezone.utc).isoformat()})
            )
            time.sleep(5)

    threading.Thread(target=report_heartbeat, daemon=True).start()
    while True:
        job_id = claim_job()
        if job_id:
            run_generation(job_id)
        else:
            time.sleep(settings.worker_poll_seconds)


if __name__ == "__main__":
    main()
