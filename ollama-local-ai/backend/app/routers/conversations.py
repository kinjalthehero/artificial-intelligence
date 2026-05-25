"""CRUD endpoints for conversations."""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.database import get_db
from app.models import (
    ConversationCreate,
    ConversationDetail,
    ConversationOut,
    MessageOut,
)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_conversation(row) -> ConversationOut:
    return ConversationOut(
        id=row["id"],
        title=row["title"],
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )


def _row_to_message(row) -> MessageOut:
    return MessageOut(
        id=row["id"],
        conversation_id=row["conversation_id"],
        role=row["role"],
        content=row["content"],
        model=row["model"],
        created_at=str(row["created_at"]),
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[ConversationOut])
async def list_conversations():
    """List all conversations, most recently updated first."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM conversations ORDER BY updated_at DESC"
        )
        rows = await cursor.fetchall()
        return [_row_to_conversation(r) for r in rows]
    finally:
        await db.close()


@router.get("/search", response_model=list[ConversationOut])
async def search_conversations(q: str = Query(..., min_length=1)):
    """Full-text search across message content, returning matching conversations."""
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            SELECT DISTINCT c.*
            FROM conversations c
            JOIN messages m ON m.conversation_id = c.id
            WHERE m.content LIKE ? OR c.title LIKE ?
            ORDER BY c.updated_at DESC
            """,
            (f"%{q}%", f"%{q}%"),
        )
        rows = await cursor.fetchall()
        return [_row_to_conversation(r) for r in rows]
    finally:
        await db.close()


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(conversation_id: str):
    """Get a conversation with all its messages."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM conversations WHERE id = ?", (conversation_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conv = ConversationDetail(
            id=row["id"],
            title=row["title"],
            created_at=str(row["created_at"]),
            updated_at=str(row["updated_at"]),
            messages=[],
        )

        msg_cursor = await db.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC",
            (conversation_id,),
        )
        msg_rows = await msg_cursor.fetchall()
        conv.messages = [_row_to_message(m) for m in msg_rows]

        return conv
    finally:
        await db.close()


@router.post("", response_model=ConversationOut, status_code=201)
async def create_conversation(body: ConversationCreate):
    """Create a new empty conversation."""
    conv_id = str(uuid.uuid4())
    title = body.title or "New conversation"

    db = await get_db()
    try:
        await db.execute(
            "INSERT INTO conversations (id, title) VALUES (?, ?)",
            (conv_id, title),
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT * FROM conversations WHERE id = ?", (conv_id,)
        )
        row = await cursor.fetchone()
        return _row_to_conversation(row)
    finally:
        await db.close()


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str):
    """Delete a conversation and all its messages (CASCADE)."""
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT id FROM conversations WHERE id = ?", (conversation_id,)
        )
        if await cursor.fetchone() is None:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Messages are removed via ON DELETE CASCADE.
        await db.execute(
            "DELETE FROM conversations WHERE id = ?", (conversation_id,)
        )
        await db.commit()
    finally:
        await db.close()
