# Lightweight MVP: Kokoro + SadTalker

Current path: creator-written dialogue → Kokoro-82M → aligned speaker WAVs → SadTalker → FFmpeg MP4.
No LLM, Ollama URL, voice recording, Unreal Engine or external inference API key is required for this path.
This integration has not yet been built or rendered on a Hugging Face GPU. Frontend build and Python static checks are separate from GPU validation.

## Deploy on Hugging Face

1. Use a Docker Space with this repository and its root Dockerfile. Assign an NVIDIA GPU; a T4 16 GB is a starting trial configuration, not a verified memory or speed guarantee. CPU-only Spaces leave talking-video generation disabled.
2. The Docker build installs two isolated environments and downloads SadTalker checkpoints. No tests or inference run during the build. The first startup/readiness check downloads Kokoro and its language assets, so model readiness can take several minutes.
3. The container starts FastAPI, one render worker and a private model service bound to `127.0.0.1:8001`. The supervisor generates an internal shared token automatically. No manually configured `SPEECH_URL`, `VIDEO_URL`, `PROVIDER_TOKEN` or `OLLAMA_URL` is needed for the bundled deployment.
4. Docker defaults enable talking-video requests, but the UI/API also require model-service readiness. `ENABLE_AI_DRAFTS=false` remains the default. Use `ENABLE_ANIMATED_RENDERS=false` to disable talking videos if validation fails.
5. Open Studio, write both characters' lines, save/approve them and create a 10-second preview first. Review pronunciation, correct speaker/lip assignment, face consistency and video/audio timing on the GPU. Then prepare approximately 120–140 words and select 60 seconds. The exact duration depends on the text; if speech is outside target ±5 seconds, the job fails with its measured duration so the creator can edit and resubmit. Words are never silently cut or rewritten.
6. Preview/download the latest submitted job directly in Studio. There is no separate Videos or Settings page. Saved conversations persist in SQLite; the inline current-job selection resets on browser refresh.

HF container disk is not a durable backup. For storage that survives rebuilds, attach persistent storage and set `DATABASE_URL=sqlite:////data/app.db`, `ASSETS_DIR=/data/assets`, and optionally `HF_HOME=/data/huggingface`. Without persistent storage, rebuilding the Space can lose scripts and outputs.

The previous private-Space creation attempt was blocked by the account's PRO requirement; deployment and GPU validation still need an available Space.

## Fixed characters and saved settings

The existing generated scene is the only image. No image uploads or character editing are exposed. Runtime preprocessing divides it into left and right portraits without changing the bundled asset. Each portrait keeps its original background, and both remain visible side by side.

R.Royale uses Kokoro `af_heart`; Summer Breeze uses `af_bella`. These are distinct American English female presets, not guarantees of African-American regional identity, AAVE, calm delivery or emotional expressiveness. Auditioning them with the creator is still required. Presets are stored in character profile JSON and copied into each generation snapshot; existing profiles receive their preset during initialization. Saved pace is applied to audio, but natural-language delivery, dialect and gesture instructions are not applied by this smaller pipeline. Those UI controls remain disabled.

SadTalker runs at 256-pixel face resolution, batch size 1, full-image preprocessing, still mode and without a face enhancer. Each aligned track contains silence when the other character speaks. Animation runs sequentially in chunks of up to 10 seconds to bound per-inference frame memory. Reinitializing the model per chunk trades speed and motion continuity for lower peak memory. FFmpeg combines both characters into a 960×540 video, then the worker adds the aligned speech mix.

## Limitations to review

- Independent talking portraits, not a jointly generated shared interaction. No meaningful listening reactions or body gestures.
- Small head/facial motion; possible artifacts, silence-time mouth movement and motion resets at chunk boundaries.
- Resolution and output size do not imply high-resolution facial detail.
- A 60-second video is not expected to render in 60 seconds. Latency and peak VRAM are unmeasured.
- Same saved inputs do not guarantee bit-for-bit identical animation.
- No claim that an approved script is pronounced perfectly: listen to the full output.

## Replaceable providers

`backend/app/ai/provider_factory.py` selects the adapters. The queue snapshots provider names, character profiles and exact dialogue. New default providers are `SPEECH_PROVIDER=kokoro` and `VIDEO_PROVIDER=sadtalker`. Existing Chatterbox and InfiniteTalk adapters remain for a future return to the heavier pipeline; they require separate services and authorized voice references. Jobs reject provider mismatches rather than silently changing a saved render's model.

For an external lightweight service, start `uvicorn model_services.lightweight_service:app --host 0.0.0.0 --port 8001` with `PYTHONPATH=backend`, `PROVIDER_TOKEN`, `SADTALKER_ROOT` and `SADTALKER_PYTHON`; configure the app with matching token, both service URLs and `ENABLE_ANIMATED_RENDERS=true`. Keep this service private. The bundled Docker configuration handles this automatically.

## Upstream sources

- Kokoro model and voice list: https://huggingface.co/hexgrad/Kokoro-82M and https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md
- SadTalker source/CLI: https://github.com/OpenTalker/SadTalker (Docker pins commit `cd4c0465ae0b54a6f85af57f5c65fec9fe23e7f8`).
- SadTalker has older dependency pins; they are isolated in a separate Python environment. The container dependency installation and compatibility still need the remote Docker build.
