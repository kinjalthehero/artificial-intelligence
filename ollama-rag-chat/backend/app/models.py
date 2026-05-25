"""Pydantic request/response models for the API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Body of POST /api/chat."""

    conversation_id: Optional[str] = Field(
        default=None,
        description="Existing conversation to continue. Omit or null to start a new one.",
    )
    message: str = Field(
        ...,
        min_length=1,
        description="The user's message text.",
    )
    model: Optional[str] = Field(
        default=None,
        description="Ollama model to use. Falls back to the configured default.",
    )
    document_ids: list[str] = Field(
        default_factory=list,
        description="Document IDs to use for RAG context.",
    )


# ---------------------------------------------------------------------------
# Conversations
# ---------------------------------------------------------------------------

class ConversationCreate(BaseModel):
    """Body of POST /api/conversations (optional title)."""

    title: Optional[str] = Field(
        default="New conversation",
        description="Conversation title.",
    )


class MessageOut(BaseModel):
    """A single message returned by the API."""

    id: str
    conversation_id: str
    role: str
    content: str
    model: Optional[str] = None
    created_at: str


class ConversationOut(BaseModel):
    """Summary of a conversation (no messages)."""

    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationDetail(ConversationOut):
    """Conversation with its full message history."""

    messages: list[MessageOut] = []


# ---------------------------------------------------------------------------
# System
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    """Response for GET /api/health."""

    status: str
    ollama_connected: bool
    ollama_host: str


class ModelInfo(BaseModel):
    """Minimal model information."""

    name: str
    size: Optional[int] = None
    modified_at: Optional[str] = None


class ModelsResponse(BaseModel):
    """Response for GET /api/models."""

    models: list[ModelInfo]
    default_model: str


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------

class DocumentOut(BaseModel):
    """A document returned by the API."""

    id: str
    conversation_id: Optional[str] = None
    filename: str
    file_type: str
    chunk_count: int
    collection_name: str
    uploaded_at: str


class SourceChunk(BaseModel):
    """A source chunk returned with RAG responses."""

    document_id: str
    filename: str
    chunk_index: int
    content: str
    score: float
