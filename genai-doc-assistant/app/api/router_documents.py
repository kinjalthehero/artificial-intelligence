import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, UploadFile

from app.core.config import settings
from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.models import DocumentOut
from app.services.chunking_service import chunking_service
from app.services.document_parser import extract_text
from app.services.vector_store import vector_store
from app.utils.rate_limiter import ip_rate_limiter, get_client_ip
from app.utils.validators import validate_upload, validate_file_size

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["documents"])


def _row_to_document(row) -> DocumentOut:
    return DocumentOut(
        id=row["id"],
        filename=row["filename"],
        file_type=row["file_type"],
        file_size=row["file_size"],
        chunk_count=row["chunk_count"],
        collection_name=row["collection_name"],
        status=row["status"],
        uploaded_at=str(row["uploaded_at"]),
    )


@router.post("/upload-document", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile, request: Request):
    ip = get_client_ip(request)
    ip_rate_limiter.check("upload", ip, settings.RATE_LIMIT_UPLOAD_PER_IP, settings.RATE_LIMIT_WINDOW_SECONDS)
    suffix = validate_upload(file)
    content = await validate_file_size(file)

    doc_id = str(uuid.uuid4())
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{doc_id}{suffix}"
    file_path.write_bytes(content)

    collection_name = f"doc_{doc_id.replace('-', '_')}"

    db = await get_db()
    try:
        await db.execute(
            """INSERT INTO documents (id, filename, file_type, file_size, chunk_count, collection_name, status)
               VALUES (?, ?, ?, ?, 0, ?, 'processing')""",
            (doc_id, file.filename, suffix.lstrip("."), len(content), collection_name),
        )
        await db.commit()

        pages = extract_text(str(file_path))
        if not pages:
            file_path.unlink(missing_ok=True)
            await db.execute("UPDATE documents SET status = 'error' WHERE id = ?", (doc_id,))
            await db.commit()
            raise HTTPException(status_code=400, detail="No text content found in file")

        chunks = chunking_service.chunk_document(pages, doc_id, file.filename)
        chunk_count = await vector_store.ingest(doc_id, chunks)

        await db.execute(
            "UPDATE documents SET chunk_count = ?, status = 'ready' WHERE id = ?",
            (chunk_count, doc_id),
        )
        await db.commit()

        cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
        row = await cursor.fetchone()
        logger.info("document_uploaded", doc_id=doc_id, filename=file.filename, chunks=chunk_count)
        return _row_to_document(row)

    except HTTPException:
        raise
    except Exception as exc:
        file_path.unlink(missing_ok=True)
        vector_store.delete_collection(doc_id)
        logger.error("document_upload_failed", error=str(exc))
        raise HTTPException(status_code=500, detail=f"Failed to process document: {exc}")
    finally:
        await db.close()


@router.get("/documents", response_model=list[DocumentOut])
async def list_documents():
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM documents ORDER BY uploaded_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_document(r) for r in rows]
    finally:
        await db.close()


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: str):
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Document not found")

        vector_store.delete_collection(document_id)

        upload_dir = Path(settings.UPLOAD_DIR)
        for f in upload_dir.glob(f"{document_id}.*"):
            f.unlink(missing_ok=True)

        await db.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        await db.commit()
        logger.info("document_deleted", doc_id=document_id)
    finally:
        await db.close()
