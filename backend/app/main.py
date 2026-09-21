from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from app.config import settings
from app.bootstrap import initialize
from app.characters.character_controller import router as character_router
from app.conversations.conversation_controller import router as conversation_router
from app.scenes.scene_controller import router as scene_router
from app.generations.generation_controller import router as generation_router
from app.assets.asset_controller import router as asset_router
from app.system.system_controller import router as system_router


@asynccontextmanager
async def lifespan(app):
    initialize()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
for router in (
    character_router,
    conversation_router,
    scene_router,
    generation_router,
    asset_router,
    system_router,
):
    app.include_router(router, prefix="/api/v1")


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": settings.app_name}


# The built Vite app and API use the same origin in the Docker deployment.
frontend = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@app.get("/{path:path}", include_in_schema=False)
def frontend_app(path: str):
    if path.startswith(("api/", "health/")):
        raise HTTPException(404, "Route not found")
    candidate = (frontend / path).resolve()
    if candidate.is_relative_to(frontend.resolve()) and candidate.is_file():
        return FileResponse(candidate)
    index = frontend / "index.html"
    if not index.is_file():
        raise HTTPException(
            404, "Build the frontend or start the Vite development server"
        )
    return FileResponse(index)
