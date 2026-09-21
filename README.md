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

A React/Vite + FastAPI monorepo for directing an original two-character conversation.
The app manages reusable profiles, uploaded assets and rights records, exact scripted
or Qwen-generated dialogue, shared scenes, a persistent render queue and video review.

## Monorepo structure

```text
backend/
  app/
    characters/       # controller, service, repository, model, schema
    conversations/    # exact scripts and optional AI drafts
    scenes/           # shared image + left/right character assignment
    generations/      # snapshot jobs, separate worker and review
    assets/           # validated media upload and rights records
    ai/               # replaceable speech, video and dialogue adapters
    shared/           # storage, audio timeline, FFmpeg export
    system/           # provider configuration and connection checks
  model_services/     # deployable Chatterbox and InfiniteTalk HTTP adapters
  demo_assets/        # original AI-generated shared-scene reference
  tests/              # backend validation and real storyboard workflow
frontend/
  src/
    app/              # shell, routes and design system
    features/         # characters, conversations, scenes, generations, settings
    shared/api/       # typed requests and shared contracts
    shared/components/# dialogs, upload control, status components
  e2e/                # Playwright against the real API and worker
scripts/              # process supervisor and isolated browser-test server
docs/                 # model deployment and requirements coverage
Dockerfile            # build + API/browser tests + same-origin serving
```

Database entities use `*_model.py`; ML integrations use `*_provider.py`. Frontend
feature components use descriptive names such as `characters.page.tsx` and
`character-editor.tsx`. No model weights or secrets belong in Git.

## Development commands

Requires Node 22 and Python 3.11+. From the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
npm ci
cp .env.example .env
python scripts/start.py
```

In a second terminal run `npm run dev`. Open http://127.0.0.1:5173.
Vite proxies `/api` to FastAPI on port 8000. API docs: http://127.0.0.1:8000/docs.
`npm run build` produces a frontend served by FastAPI itself, using the same origin.

## Testing and deployment

```sh
npm run build
PYTHONPATH=backend pytest backend/tests -q
npx playwright install --with-deps chromium
npm run test:e2e
```

For this project the Docker build runs API and browser tests remotely on Hugging
Face before publishing the runtime image. CI uses the same commands. Browser tests
exercise actual HTTP endpoints, SQLite and FFmpeg; they do not fake AI inference.
`E2E_BASE_URL` may point to a disposable deployed instance instead of the isolated
local test server. E2E creates test records, so do not target valuable production data.

Deploy this repo as a **private Docker Space**, initially on CPU hardware. This account currently requires Hugging Face PRO
for a Docker Space, even for the `cpu-basic` tier.
The private creator-workspace assumption is important: this MVP does not implement
multi-user authentication or tenant isolation. Keep GPU services private and use
`PROVIDER_TOKEN` authentication. Paid GPU hardware is a separate deployment decision.

Default disk is ephemeral. For persistent reuse across Space rebuilds, attach
persistent storage and set `DATABASE_URL=sqlite:////data/app.db` and
`ASSETS_DIR=/data/assets`. Download outputs and saved-input manifests before a
restart if persistent storage is not attached. The schema is an initial release;
future schema changes need migrations rather than reusing an incompatible old DB.

## What is implemented

- Saved, versioned original character profiles; distinct voice/image references.
- Region, AAVE preferences, slang, vocabulary, pronunciation notes, cadence,
  code-switching, expressiveness, pace and gesture settings.
- Exact scripted dialogue and optional structured Qwen drafts via Ollama.
- Uploaded shared scene image, left/right assignment and creator approval.
- Immutable generation snapshots, worker progress, failure/retry and queued cancellation.
- Chatterbox/InfiniteTalk service adapters; silence-aligned voice tracks and MP4 export.
- Silent storyboard export, explicitly identified as having no speech or animation.
- Asset ownership records, rights attestation and revocation.
- Creator review of words, identity, lip-sync and reactions; saved-input JSON export.
- Responsive frontend, build checks, API tests and browser E2E tests.

## What still requires the real model environment

See [GPU model setup](docs/model-services.md). An animated demo needs deployed
Chatterbox and InfiniteTalk weights, GPU capacity, approved images and two authorized
voice references. Generating a storyboard does **not** satisfy the animated demo.
The initial video adapter targets 480p; realistic 60-second motion and a higher
resolution deliverable must be verified on GPU. AAVE/accent controls are saved
preferences rather than a guarantee that the speech model can perform them.

The included shared-scene reference is AI-generated and fictional. It is a starting
proposal, not client-approved likeness or voice material. Real-person face uploads
are disabled under this prototype's rights policy. Voice uploads require explicit
rights attestation; this is not an automated identity-verification system.

## Disabled MVP controls

AI drafts, animated conversation rendering, and their speech/performance controls
are disabled by default. Hover, keyboard-focus, or tap a disabled area to see why.
Manual scripts, profiles, uploads, scene setup and saved outputs stay available.
Storyboards and render retries are disabled when the worker heartbeat is missing.
Existing profile and performance values are preserved while their controls are locked.

The backend also blocks AI-draft and animated-generation requests, including retries.
After validating the corresponding model integrations, explicitly set
`ENABLE_AI_DRAFTS=true` and/or `ENABLE_ANIMATED_RENDERS=true`, configure the required
service URLs and restart the backend. A successful connection check alone does not
enable a feature. Free-form voice-direction instructions remain disabled because
the current speech adapter does not apply them.
