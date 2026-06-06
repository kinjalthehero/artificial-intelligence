"""
Input Validation — Security Boundary
======================================
Validates all user input at the API boundary before processing.

Why validate at the boundary?
- Prevents malicious file uploads (only allowed formats pass)
- Limits resource consumption (file size cap, query length cap)
- Fails fast with clear error messages instead of cryptic internal errors
- Security best practice: never trust user input

These validators are called at the start of each API endpoint before
any processing begins.
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.core.config import settings

# Whitelist of allowed file extensions — only these can be uploaded
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx", ".xls", ".json", ".yaml", ".yml"}


def validate_upload(file: UploadFile) -> str:
    """Validate an uploaded file's name and extension.

    Returns the file extension (e.g., ".pdf") if valid.
    Raises HTTP 400 if the filename is missing or the extension is not allowed.
    """
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
    """Read and validate the uploaded file size.

    Returns the file content as bytes if within the size limit (10 MB).
    Raises HTTP 400 if the file is too large.
    """
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        max_mb = settings.MAX_UPLOAD_SIZE / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {max_mb:.0f} MB",
        )
    return content


def validate_query(message: str) -> None:
    """Validate a chat query's length. Raises HTTP 400 if too long."""
    if len(message) > settings.MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Maximum: {settings.MAX_QUERY_LENGTH} characters",
        )
