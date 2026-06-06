"""
FastAPI Application Entry Point
================================
This is the main entry point for the GenAI Document Assistant backend.

Why FastAPI?
- Async support (needed for non-blocking LLM API calls and database operations)
- Built-in request validation via Pydantic models
- Auto-generated API docs at /docs (Swagger UI)
- Native support for Server-Sent Events (SSE) streaming
- High performance (one of the fastest Python web frameworks)

In production, FastAPI also serves the pre-built React frontend as static files,
so a single Docker container hosts both the API and the UI.
"""

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.core.logging_config import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown lifecycle hook.

    On startup: initializes the SQLite database schema (creates tables if they don't exist)
    and ensures data directories exist. This runs once when the server starts.
    On shutdown: cleanup (handled automatically by aiosqlite and ChromaDB).
    """
    logger.info("starting_up", environment=settings.ENVIRONMENT)
    await init_db()
    yield
    logger.info("shutting_down")


app = FastAPI(
    title="GenAI Document Assistant",
    description="AI-powered document Q&A with RAG pipeline and agent-based reasoning.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS (Cross-Origin Resource Sharing) middleware:
# Required when the React frontend (running on localhost:3000 during development)
# makes API calls to the backend (running on localhost:8000). Without CORS,
# browsers block cross-origin requests for security. In production (Docker),
# both frontend and backend are on the same origin, so CORS isn't strictly needed,
# but we keep it configured for flexibility.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and register all API routers
# Each router handles a specific domain (health, documents, chat, conversations)
from app.api import router_health, router_documents, router_chat, router_conversations  # noqa: E402

app.include_router(router_health.router)
app.include_router(router_documents.router)
app.include_router(router_chat.router)
app.include_router(router_conversations.router)


# Global exception handler: catches any unhandled exceptions and returns a clean
# 500 error instead of leaking stack traces to the client. This is a security
# best practice — internal error details should only go to logs, not to users.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# Static file serving for the React frontend:
# In production, the React app is pre-built (npm run build) into frontend/dist/.
# FastAPI serves these static files directly, so the entire app (API + UI) runs
# from a single server — no need for a separate web server like Nginx.
# The SPA (Single Page Application) fallback returns index.html for any unknown
# path, letting React Router handle client-side routing.
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend" / "dist"

if FRONTEND_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(FRONTEND_DIR / "index.html")
else:
    # If no built frontend exists, show a JSON message pointing to the docs
    @app.get("/", tags=["root"])
    async def root():
        return {
            "app": "GenAI Document Assistant",
            "docs": "/docs",
            "health": "/api/health-check",
            "note": "Run 'npm run build' in frontend/ to enable the UI",
        }


if __name__ == "__main__":
    import uvicorn

    # PORT env var is set by Render.com and other cloud platforms
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("main:app", host=settings.HOST, port=port, reload=settings.ENVIRONMENT == "development")
