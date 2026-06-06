"""
Pydantic Request/Response Models
=================================
Defines the data shapes for all API requests and responses.

Why Pydantic?
- Automatic validation: FastAPI uses these models to validate incoming JSON bodies
  and serialize outgoing responses. Invalid data returns a clear 422 error.
- Type safety: each field has a defined type, making the code self-documenting
- Auto-generated API docs: FastAPI uses these models to build the Swagger UI at /docs
"""

from typing import Optional

from pydantic import BaseModel, Field


# --- Request Models (incoming data from the frontend) ---

class AskQuestionRequest(BaseModel):
    """Body of POST /api/ask-questions — the user's chat message."""
    conversation_id: Optional[str] = None  # None = start a new conversation
    message: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)  # Which uploaded docs to search


class ConversationCreate(BaseModel):
    """Body of POST /api/conversations — create a new empty conversation."""
    title: Optional[str] = Field(default="New conversation")


# --- Response Models (outgoing data to the frontend) ---

class AgentStep(BaseModel):
    """One step in the 5-agent pipeline, shown in the AgentWorkflow UI component."""
    agent: str  # "planner", "retriever", "reasoning", "response", "verification"
    action: str  # What the agent did (e.g., "Decomposed query into retrieval strategy")
    result: str  # Summary of the result
    duration_ms: int  # How long this step took (displayed in the progress bar)


class MessageOut(BaseModel):
    """A single chat message returned by the API."""
    id: str
    conversation_id: str
    role: str  # "user" or "assistant"
    content: str
    agent_steps: Optional[str] = None  # JSON string of AgentStep list
    sources: Optional[str] = None  # JSON string of source chunks used
    created_at: str


class ConversationOut(BaseModel):
    """Summary of a conversation (shown in the sidebar list)."""
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationDetail(ConversationOut):
    """Conversation with its full message history (when user clicks a conversation)."""
    messages: list[MessageOut] = []


class HealthCheckResponse(BaseModel):
    """Response for GET /api/health-check — used by the frontend to show connection status."""
    status: str
    gemini_connected: bool  # Whether the Gemini API is reachable
    version: str
    documents_count: int
    environment: str


class DocumentOut(BaseModel):
    """An uploaded document returned by the API."""
    id: str
    filename: str
    file_type: str  # "pdf", "csv", "xlsx", etc.
    file_size: int  # Bytes
    chunk_count: int  # How many text chunks were created
    collection_name: str  # ChromaDB collection name (doc_{uuid})
    status: str  # "processing", "ready", or "error"
    uploaded_at: str


class SourceChunk(BaseModel):
    """A source chunk returned with RAG responses — shown in the "Show sources" panel."""
    document_id: str
    filename: str
    chunk_index: int
    content: str  # Preview of the chunk text
    score: float  # Cosine similarity score (0.0 to 1.0, higher = more relevant)
