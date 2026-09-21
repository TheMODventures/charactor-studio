# GPU model services

The web application and its SQLite worker can run in one CPU Docker Space. GPU
inference lives in private services reached through `SPEECH_URL` and `VIDEO_URL`.
Keep the services private or protect them with a random `PROVIDER_TOKEN` set in
both the app and model services. For Hugging Face private-Space routing, the
bearer credential also needs permission to access that Space (or expose the model
service behind a separate authenticated gateway). Never commit tokens or pass them
to the browser.

## Chatterbox

Use the official Chatterbox installation in its own environment:
https://github.com/resemble-ai/chatterbox

Add FastAPI, uvicorn and python-multipart to that environment. Set `TTS_DEVICE=cuda`
and `PROVIDER_TOKEN`, then run from this repository:

```sh
uvicorn backend.model_services.chatterbox_service:app --host 0.0.0.0 --port 7860
```

The first synthesis loads weights. Supply two distinct authorized 3–30 second WAV
references. Requests preserve script text; Chatterbox may still mispronounce or add
sounds, which must be caught in the creator review. Slang, pronunciation and region
fields guide draft writing and review, not guaranteed acoustic dialect transfer.

## InfiniteTalk

Install the official repository and its pinned CUDA/PyTorch dependencies separately:
https://github.com/MeiGen-AI/InfiniteTalk

Download these model components into the expected layout:

```sh
hf download Wan-AI/Wan2.1-I2V-14B-480P --local-dir /models/Wan2.1-I2V-14B-480P
hf download TencentGameMate/chinese-wav2vec2-base --local-dir /models/chinese-wav2vec2-base
hf download MeiGen-AI/InfiniteTalk --local-dir /models/InfiniteTalk
```

Set `INFINITETALK_ROOT` to the official checkout and `VIDEO_WEIGHTS_DIR=/models`.
Verify the upstream audio encoder requirements and any revised checkpoint layout
against the checked-out revision. Add FastAPI, uvicorn and python-multipart, then run:

```sh
uvicorn backend.model_services.infinitetalk_service:app --host 0.0.0.0 --port 7860
```

The adapter calls the documented multi-person CLI using `audio_type=para`, one
shared scene image and silence-aligned per-person tracks. Its initial output is
480p. Raising resolution, GPU memory tuning and final performance quality must be
benchmarked on the selected GPU; the web build tests do not establish those claims.
Model timeout and the application's `PROVIDER_TIMEOUT` must accommodate the full
render. The app retains raw speech, timelines, separate tracks and render outputs.

## Conversation drafts

Run Ollama separately, pull `qwen3:8b`, and point `OLLAMA_URL` to it. Creator-written
scripts work without Ollama. Profile data is passed to the model on each draft.

## Required GPU acceptance test

1. Approve the fictional shared image and two authorized voice references.
2. Generate a 10-second exchange and verify speaker-to-face assignment.
3. Check transcription manually, facial identity, gestures and silent reactions.
4. Tune pace/word count; the worker rejects speech more than 5 seconds from target.
5. Generate and review the full approximately 60-second take before client delivery.

No GPU inference has been claimed solely from a successful application test.
