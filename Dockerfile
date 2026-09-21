# Hugging Face Docker Space. Inference runs only on the assigned GPU at runtime.
FROM node:22-bookworm AS frontend
WORKDIR /workspace
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
RUN npm ci
COPY frontend frontend
RUN npm run build

FROM python:3.10-slim-bookworm
WORKDIR /workspace
RUN apt-get update && apt-get install -y --no-install-recommends \
    git wget ffmpeg espeak-ng libsndfile1 libgl1 libglib2.0-0 build-essential \
    && rm -rf /var/lib/apt/lists/*

# SadTalker's older dependencies stay separate from Kokoro and FastAPI.
ARG SADTALKER_REF=cd4c0465ae0b54a6f85af57f5c65fec9fe23e7f8
RUN git clone https://github.com/OpenTalker/SadTalker.git /opt/SadTalker \
    && cd /opt/SadTalker && git checkout "$SADTALKER_REF"
COPY backend/model_services/requirements-sadtalker.txt /tmp/requirements-sadtalker.txt
RUN python -m venv /opt/sadtalker-venv \
    && /opt/sadtalker-venv/bin/pip install --no-cache-dir 'setuptools<70' wheel \
    && /opt/sadtalker-venv/bin/pip install --no-cache-dir \
       torch==1.13.1+cu117 torchvision==0.14.1+cu117 \
       --extra-index-url https://download.pytorch.org/whl/cu117 \
    && /opt/sadtalker-venv/bin/pip install --no-cache-dir --no-build-isolation -r /tmp/requirements-sadtalker.txt
RUN cd /opt/SadTalker && bash scripts/download_models.sh \
    && test -s checkpoints/SadTalker_V0.0.2_256.safetensors \
    && test -s checkpoints/mapping_00109-model.pth.tar

COPY backend/requirements.txt backend/requirements.txt
COPY backend/model_services/requirements-lightweight.txt backend/model_services/requirements-lightweight.txt
RUN pip install --no-cache-dir torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r backend/requirements.txt -r backend/model_services/requirements-lightweight.txt
RUN useradd -m -u 1000 studio
COPY --chown=studio:studio backend backend
COPY --chown=studio:studio scripts scripts
COPY --from=frontend --chown=studio:studio /workspace/frontend/dist frontend/dist
# /workspace itself must be writable: the worker heartbeat is written beside
# ASSETS_DIR, and /data is pre-created so persistent-storage overrides work.
RUN mkdir -p data assets /home/studio/.cache /data \
    && chown studio:studio /workspace /data \
    && chown -R studio:studio data assets /home/studio/.cache /opt/SadTalker
USER studio
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/workspace/backend HOST=0.0.0.0 PORT=7860 \
    DATABASE_URL=sqlite:////workspace/data/app.db ASSETS_DIR=/workspace/assets \
    START_MODEL_SERVICE=true ENABLE_ANIMATED_RENDERS=true ENABLE_AI_DRAFTS=false \
    SPEECH_PROVIDER=kokoro VIDEO_PROVIDER=sadtalker OLLAMA_URL="" \
    SADTALKER_ROOT=/opt/SadTalker SADTALKER_PYTHON=/opt/sadtalker-venv/bin/python \
    PROVIDER_TIMEOUT=14400 VIDEO_TIMEOUT=3600 HF_HOME=/home/studio/.cache/huggingface
EXPOSE 7860
CMD ["python", "scripts/start.py"]
