import json
import uuid

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.core.database import get_db
from app.core.logging_config import get_logger
from app.core.models import AskQuestionRequest
from app.services.gemini_service import gemini_service
from app.services.rag_service import rag_service
from app.utils.validators import validate_query

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

MAX_CONTEXT_MESSAGES = 20


async def _ensure_conversation(db, conversation_id: str | None, first_message: str) -> str:
    if conversation_id:
        cursor = await db.execute(
            "SELECT id FROM conversations WHERE id = ?", (conversation_id,)
        )
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation_id

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
    db, conversation_id: str, role: str, content: str,
    agent_steps: str | None = None, sources: str | None = None,
) -> str:
    msg_id = str(uuid.uuid4())
    await db.execute(
        """INSERT INTO messages (id, conversation_id, role, content, agent_steps, sources)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (msg_id, conversation_id, role, content, agent_steps, sources),
    )
    await db.execute(
        "UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (conversation_id,),
    )
    await db.commit()
    return msg_id


async def _get_context_messages(db, conversation_id: str) -> list[dict]:
    cursor = await db.execute(
        """SELECT role, content FROM messages
           WHERE conversation_id = ?
           ORDER BY created_at DESC
           LIMIT ?""",
        (conversation_id, MAX_CONTEXT_MESSAGES),
    )
    rows = await cursor.fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


@router.post("/ask-questions")
async def ask_questions(body: AskQuestionRequest, request: Request):
    validate_query(body.message)

    db = await get_db()

    rag_chunks = []
    agent_steps_json = None
    try:
        conversation_id = await _ensure_conversation(db, body.conversation_id, body.message)
        await _save_message(db, conversation_id, "user", body.message)
        context = await _get_context_messages(db, conversation_id)

        if body.document_ids:
            rag_chunks = await rag_service.retrieve(body.message, body.document_ids)

            if rag_chunks:
                try:
                    from app.agents.orchestrator import orchestrator
                    agent_result = await orchestrator.process_query(
                        body.message, body.document_ids, rag_chunks
                    )
                    final_answer = agent_result["answer"]
                    agent_steps_json = json.dumps(agent_result["steps"])
                    rag_chunks = agent_result.get("chunks", rag_chunks)
                except Exception as agent_err:
                    logger.warning("agent_pipeline_fallback", error=str(agent_err))
                    augmented = rag_service.build_rag_prompt(body.message, rag_chunks)
                    context[-1] = {"role": "user", "content": augmented}
                    final_answer = None
            else:
                final_answer = None
        else:
            final_answer = None

    except HTTPException:
        await db.close()
        raise
    except Exception as exc:
        await db.close()
        raise HTTPException(status_code=500, detail=str(exc))

    async def event_generator():
        full_response = ""
        try:
            yield {"data": json.dumps({"type": "conversation_id", "value": conversation_id})}

            if final_answer is not None:
                if agent_steps_json:
                    steps = json.loads(agent_steps_json)
                    for step in steps:
                        yield {"data": json.dumps({"type": "agent_step", "value": step})}

                for char_batch in _chunk_text_for_streaming(final_answer):
                    if await request.is_disconnected():
                        break
                    full_response += char_batch
                    yield {"data": json.dumps({"type": "token", "value": char_batch})}
            else:
                system_prompt = rag_service.get_system_prompt() if rag_chunks else "You are a helpful AI assistant."
                async for token in gemini_service.stream_chat(system_prompt, context):
                    if await request.is_disconnected():
                        break
                    full_response += token
                    yield {"data": json.dumps({"type": "token", "value": token})}

            await _save_message(
                db, conversation_id, "assistant", full_response,
                agent_steps=agent_steps_json,
                sources=json.dumps([
                    {"document_id": c["document_id"], "filename": c["filename"],
                     "chunk_index": c["chunk_index"], "content": c["content"][:200],
                     "score": c["score"]}
                    for c in rag_chunks
                ]) if rag_chunks else None,
            )

            if rag_chunks:
                sources = [
                    {"document_id": c["document_id"], "filename": c["filename"],
                     "chunk_index": c["chunk_index"], "page": c.get("page", 1),
                     "content": c["content"][:200], "score": c["score"]}
                    for c in rag_chunks
                ]
                yield {"data": json.dumps({"type": "sources", "value": sources})}

            if agent_steps_json:
                yield {"data": json.dumps({"type": "agent_steps", "value": json.loads(agent_steps_json)})}

            yield {"data": json.dumps({"type": "done"})}

        except Exception as exc:
            if full_response:
                try:
                    await _save_message(db, conversation_id, "assistant", full_response)
                except Exception:
                    pass
            yield {"data": json.dumps({"type": "error", "value": str(exc)})}
        finally:
            await db.close()

    return EventSourceResponse(event_generator())


def _chunk_text_for_streaming(text: str, chunk_size: int = 8) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
