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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.api import router_health, router_documents, router_chat, router_conversations  # noqa: E402

app.include_router(router_health.router)
app.include_router(router_documents.router)
app.include_router(router_chat.router)
app.include_router(router_conversations.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


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

    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("main:app", host=settings.HOST, port=port, reload=settings.ENVIRONMENT == "development")
