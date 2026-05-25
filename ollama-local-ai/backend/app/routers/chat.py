"""Chat endpoint with Server-Sent Events streaming."""

import json
import uuid

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.database import get_db
from app.models import ChatRequest
from app.services.ollama_service import ollama_service
from app.services.rag_service import rag_service

router = APIRouter(prefix="/api", tags=["chat"])

# Maximum number of historical messages sent as context to Ollama.
MAX_CONTEXT_MESSAGES = 20


async def _ensure_conversation(
    db, conversation_id: str | None, first_message: str
) -> str:
    """Return an existing conversation id or create a new one.

    When creating, the title is derived from the first ~50 characters of the
    user's message.
    """
    if conversation_id:
        cursor = await db.execute(
            "SELECT id FROM conversations WHERE id = ?", (conversation_id,)
        )
        if await cursor.fetchone() is None:
            raise HTTPException(
                status_code=404, detail="Conversation not found"
            )
        return conversation_id

    # Auto-generate title from first message.
    title = first_message[:50].strip()
    if len(first_message) > 50:
        title += "..."

    conv_id = str(uuid.uuid4())
    await db.execute(
        "INSERT INTO conversations (id, title) VALUES (?, ?)",
        (conv_id, title),
    )
    await db.commit()
    return conv_id


async def _save_message(
    db, conversation_id: str, role: str, content: str, model: str | None = None
) -> str:
    """Insert a message and update the conversation's updated_at timestamp."""
    msg_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO messages (id, conversation_id, role, content, model)
           VALUES (?, ?, ?, ?, ?)""",
        (msg_id, conversation_id, role, content, model),
    )
    await db.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,),
    )
    await db.commit()
    return msg_id


async def _get_context_messages(db, conversation_id: str) -> list[dict]:
    """Fetch the last N messages for the conversation in chronological order."""
    cursor = await db.execute(
        """SELECT role, content FROM messages
           WHERE conversation_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (conversation_id, MAX_CONTEXT_MESSAGES),
    )
    rows = await cursor.fetchall()
    # Reverse so oldest is first (chronological order for the LLM).
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


@router.post("/chat")
async def chat(body: ChatRequest, request: Request):
    """Stream a chat response via Server-Sent Events.

    Event types emitted:
      - ``conversation_id`` — the id of the (possibly new) conversation
      - ``token``           — a single token of the assistant's reply
      - ``done``            — signals the stream is complete
      - ``error``           — if something goes wrong mid-stream
    """
    model = body.model or settings.DEFAULT_MODEL

    # Verify Ollama is reachable before opening the SSE stream.
    if not await ollama_service.is_healthy():
        raise HTTPException(
            status_code=503,
            detail=f"Ollama is not reachable at {settings.OLLAMA_HOST}",
        )

    db = await get_db()

    rag_chunks = []
    try:
        conversation_id = await _ensure_conversation(
            db, body.conversation_id, body.message
        )

        # Persist the user message.
        await _save_message(db, conversation_id, "user", body.message)

        # Build the message list for Ollama (history + new user message is
        # already included because we just saved it).
        context = await _get_context_messages(db, conversation_id)

        # If document_ids provided, retrieve relevant chunks and augment the
        # last user message with RAG context.
        if body.document_ids:
            rag_chunks = await rag_service.query(body.message, body.document_ids)
            if rag_chunks:
                augmented = rag_service.build_rag_prompt(body.message, rag_chunks)
                context[-1] = {"role": "user", "content": augmented}
    except HTTPException:
        await db.close()
        raise
    except Exception as exc:
        await db.close()
        raise HTTPException(status_code=500, detail=str(exc))

    # --- SSE generator ---------------------------------------------------

    async def event_generator():
        full_response = ""
        try:
            # 1. Emit the conversation id so the client can track it.
            yield {
                "data": json.dumps(
                    {"type": "conversation_id", "value": conversation_id}
                )
            }

            # 2. Stream tokens from Ollama.
            async for token in ollama_service.stream_chat(context, model=model):
                # If the client disconnected, stop generating.
                if await request.is_disconnected():
                    break
                full_response += token
                yield {
                    "data": json.dumps({"type": "token", "value": token})
                }

            # 3. Save the complete assistant response.
            await _save_message(
                db, conversation_id, "assistant", full_response, model
            )

            # 4. Emit source citations if RAG was used.
            if rag_chunks:
                sources = [
                    {
                        "document_id": c["document_id"],
                        "filename": c["filename"],
                        "chunk_index": c["chunk_index"],
                        "page": c.get("page", 1),
                        "content": c["content"][:200],
                        "score": c["score"],
                    }
                    for c in rag_chunks
                ]
                yield {
                    "data": json.dumps({"type": "sources", "value": sources})
                }

            # 5. Signal completion.
            yield {"data": json.dumps({"type": "done"})}

        except Exception as exc:
            # Best-effort: save whatever we collected so far.
            if full_response:
                try:
                    await _save_message(
                        db, conversation_id, "assistant", full_response, model
                    )
                except Exception:
                    pass
            yield {
                "data": json.dumps(
                    {"type": "error", "value": str(exc)}
                )
            }
        finally:
            await db.close()

    return EventSourceResponse(event_generator())
