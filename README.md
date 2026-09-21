---
title: Character Studio
emoji: 🎬
colorFrom: purple
colorTo: pink
sdk: docker
app_port: 7860
pinned: false
---

# Character Studio

A React/Vite + FastAPI MVP using two fixed fictional characters and the included generated image.
The UI is a single Studio page: write exact dialogue, save/approve it, create a preview and download the result.
Image uploads, character editing, Settings and Videos pages are not exposed.

## Current small-model pipeline

**Written dialogue → Kokoro-82M → SadTalker → FFmpeg.** No Ollama, voice recordings or external AI API keys are required.
R.Royale and Summer Breeze use different saved voice presets. Each portrait is animated independently and shown beside the other; natural shared reactions, body gestures and detailed dialect controls are not implemented.

The root Dockerfile prepares the frontend, backend and bundled model service for a Hugging Face NVIDIA GPU Space.
It does not run tests or inference at build time. The talking-video button requires model-service readiness.
**Remote Docker build and GPU output quality remain unverified.** See [deployment steps and limitations](docs/lightweight-mvp.md).

## Structure

```text
backend/app/
  characters/       # saved character profiles, voice presets
  conversations/    # creator-written dialogue; optional AI adapter
  scenes/           # fixed cast and reference image
  generations/      # immutable input snapshots, queue, worker
  assets/           # asset records and downloads
  ai/               # provider factory and replaceable model adapters
  shared/           # storage, audio alignment, FFmpeg export
  system/           # availability checks
backend/model_services/  # Kokoro/SadTalker service; legacy model adapters
backend/demo_assets/     # fixed generated scene
frontend/src/
  app/                   # app shell and styles
  features/              # Studio, dialogue and scene components
  shared/                # API client, types and common components
scripts/start.py         # supervises API, worker and optional model service
docs/lightweight-mvp.md  # deployment and current capability details
```

Backend modules use controller/service/repository/model/schema files. ML models use provider files.
The local SQLite database is created automatically; no separate database server is needed.
Attach persistent storage on Hugging Face if scripts and outputs must survive a rebuild.

## Frontend development

```sh
npm ci
npm run dev
```

Vite proxies `/api` to the backend. Build with `npm run build`.
For backend-only development, install `backend/requirements.txt`, copy `.env.example` to `.env`,
and run `python scripts/start.py` with the backend virtual environment active.
Local defaults disable model inference; the GPU Docker deployment supplies its own defaults.

Legacy test files and heavier model adapters remain in the repository. Tests have not been updated or run for this simplified MVP.
The older [model-services document](docs/model-services.md) and [requirements coverage](docs/requirements-coverage.md) describe the previous heavier design; use the lightweight guide for the current implementation.
