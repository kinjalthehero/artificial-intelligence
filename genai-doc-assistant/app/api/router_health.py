from fastapi import APIRouter

from app.core.config import settings
from app.core.database import get_db
from app.core.models import HealthCheckResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health-check", response_model=HealthCheckResponse)
async def health_check():
    gemini_ok = False
    try:
        from app.services.gemini_service import gemini_service
        gemini_ok = await gemini_service.is_healthy()
    except Exception:
        pass

    doc_count = 0
    try:
        db = await get_db()
        try:
            cursor = await db.execute("SELECT COUNT(*) FROM documents")
            row = await cursor.fetchone()
            doc_count = row[0] if row else 0
        finally:
            await db.close()
    except Exception:
        pass

    return HealthCheckResponse(
        status="ok",
        gemini_connected=gemini_ok,
        version="1.0.0",
        documents_count=doc_count,
        environment=settings.ENVIRONMENT,
    )
