from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx", ".xls", ".json", ".yaml", ".yml"}


def validate_upload(file: UploadFile) -> str:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    return suffix


async def validate_file_size(file: UploadFile) -> bytes:
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_mb:.0f} MB",
        )
    return content


def validate_query(message: str) -> None:
    if len(message) > settings.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Maximum: {settings.MAX_QUERY_LENGTH} characters",
        )
