"""Document upload, listing, and deletion endpoints."""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import settings
from app.database import get_db
from app.models import DocumentOut
from app.services.document_parser import extract_text
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {".pdf", ".txt", ".md", ".markdown"}


def _row_to_document(row) -> DocumentOut:
    return DocumentOut(
        id=row["id"],
        conversation_id=row["conversation_id"],
        filename=row["filename"],
        file_type=row["file_type"],
        chunk_count=row["chunk_count"],
        collection_name=row["collection_name"],
        uploaded_at=str(row["uploaded_at"]),
    )


@router.post("/upload", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile):
    """Upload a file, parse it, chunk it, embed it, and store in ChromaDB."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. Allowed: {', '.join(sorted(ALLOWED_TYPES))}",
        )

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50 MB)")

    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    doc_id = str(uuid.uuid4())
    file_path = upload_dir / f"{doc_id}{suffix}"
    file_path.write_bytes(content)

    try:
        pages = extract_text(str(file_path))
        if not pages:
            file_path.unlink(missing_ok=True)
            raise HTTPException(status_code=400, detail="No text content found in file")

        chunk_count = await rag_service.ingest_document(doc_id, file.filename, pages)

        collection_name = f"doc_{doc_id.replace('-', '_')}"
        db = await get_db()
        try:
            await db.execute(
                """INSERT INTO documents (id, filename, file_type, chunk_count, collection_name)
                   VALUES (?, ?, ?, ?, ?)""",
                (doc_id, file.filename, suffix.lstrip("."), chunk_count, collection_name),
            )
            await db.commit()
            cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = await cursor.fetchone()
            return _row_to_document(row)
        finally:
            await db.close()

    except HTTPException:
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        rag_service.delete_collection(doc_id)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {exc}")


@router.get("", response_model=list[DocumentOut])
async def list_documents():
    """List all uploaded documents."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_document(r) for r in rows]
    finally:
        await db.close()


@router.delete("/{document_id}", status_code=204)
async def delete_document(document_id: str):
    """Delete a document, its vectors, and its uploaded file."""
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found")

        rag_service.delete_collection(document_id)

        upload_dir = Path(settings.UPLOAD_DIR)
        for f in upload_dir.glob(f"{document_id}.*"):
            f.unlink(missing_ok=True)

        await db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        await db.commit()
    finally:
        await db.close()
