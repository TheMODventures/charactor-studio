# Docker Space: build and test without running inference on the build machine.
FROM node:22-bookworm AS validate
WORKDIR /workspace
RUN apt-get update && apt-get install -y python3 python3-venv && rm -rf /var/lib/apt/lists/*
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package.json
RUN npm ci
COPY backend/requirements.txt backend/requirements-dev.txt backend/
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r backend/requirements-dev.txt
COPY frontend frontend
COPY backend backend
COPY scripts scripts
RUN npm run build
RUN PYTHONPATH=backend pytest backend/tests -q
RUN npx playwright install --with-deps chromium
RUN npm run test:e2e

FROM python:3.12-slim
WORKDIR /workspace
RUN useradd -m -u 1000 studio
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY --chown=studio:studio backend backend
COPY --chown=studio:studio scripts scripts
COPY --from=validate --chown=studio:studio /workspace/frontend/dist frontend/dist
COPY --from=validate --chown=studio:studio /workspace/frontend/playwright-report test-results/browser-report
RUN mkdir -p data assets && chown -R studio:studio data assets
USER studio
ENV PYTHONUNBUFFERED=1 PYTHONPATH=/workspace/backend HOST=0.0.0.0 PORT=7860 DATABASE_URL=sqlite:////workspace/data/app.db ASSETS_DIR=/workspace/assets
EXPOSE 7860
CMD ["python", "scripts/start.py"]
