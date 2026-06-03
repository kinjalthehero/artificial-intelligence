from typing import Optional

from pydantic import BaseModel, Field


class AskQuestionRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(..., min_length=1, max_length=2000)
    document_ids: list[str] = Field(default_factory=list)


class AgentStep(BaseModel):
    agent: str
    action: str
    result: str
    duration_ms: int


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(default="New conversation")


class MessageOut(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    agent_steps: Optional[str] = None
    sources: Optional[str] = None
    created_at: str


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class ConversationDetail(ConversationOut):
    messages: list[MessageOut] = []


class HealthCheckResponse(BaseModel):
    status: str
    gemini_connected: bool
    version: str
    documents_count: int
    environment: str


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    collection_name: str
    status: str
    uploaded_at: str


class SourceChunk(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    content: str
    score: float
