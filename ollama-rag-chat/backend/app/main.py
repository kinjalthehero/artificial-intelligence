"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import init_db
from app.routers import chat, conversations, documents, system


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle hook.

    - On startup: initialize the SQLite database schema.
    - On shutdown: nothing special for now (aiosqlite handles cleanup).
    """
    await init_db()
    yield


app = FastAPI(
    title="Ollama RAG Chat",
    description="Locally-deployed AI chat API backed by Ollama.",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(conversations.router)
app.include_router(documents.router)
app.include_router(system.router)


FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:

    @app.get("/", tags=["root"])
    async def root():
        return {
            "app": "Ollama RAG Chat",
            "docs": "/docs",
            "health": "/api/health",
            "note": "Run 'npm run build' in frontend/ to enable the UI",
        }
