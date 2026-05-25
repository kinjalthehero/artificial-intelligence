"""System endpoints: health check and model listing."""

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import HealthResponse, ModelInfo, ModelsResponse
from app.services.ollama_service import ollama_service

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check that the backend is running and Ollama is reachable."""
    connected = await ollama_service.is_healthy()
    return HealthResponse(
        status="ok",
        ollama_connected=connected,
        ollama_host=settings.OLLAMA_HOST,
    )


@router.get("/models", response_model=ModelsResponse)
async def list_models():
    """List locally available Ollama models."""
    try:
        raw_models = await ollama_service.list_models()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot reach Ollama at {settings.OLLAMA_HOST}: {exc}",
        )

    models = [
        ModelInfo(
            name=m["name"],
            size=m.get("size"),
            modified_at=m.get("modified_at"),
        )
        for m in raw_models
    ]

    return ModelsResponse(models=models, default_model=settings.DEFAULT_MODEL)
