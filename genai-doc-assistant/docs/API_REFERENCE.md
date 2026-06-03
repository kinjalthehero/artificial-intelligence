# API Reference

**Live API**: https://genai-doc-assistant-slnu.onrender.com/api

**Swagger UI**: https://genai-doc-assistant-slnu.onrender.com/docs

Base URL: `/api`

## Health Check

### `GET /api/health-check`

Returns system health status.

**Response:**
```json
{
  "status": "ok",
  "gemini_connected": true,
  "version": "1.0.0",
  "documents_count": 5,
  "environment": "production"
}
```

## Documents

### `POST /api/upload-document`

Upload and process a document.

**Request:** `multipart/form-data` with `file` field

**Supported formats:** PDF, TXT, CSV, XLSX, XLS, JSON, YAML, YML

**Max size:** 10 MB

**Response (201):**
```json
{
  "id": "uuid",
  "filename": "report.pdf",
  "file_type": "pdf",
  "file_size": 524288,
  "chunk_count": 15,
  "collection_name": "doc_uuid",
  "status": "ready",
  "uploaded_at": "2024-01-01T00:00:00"
}
```

### `GET /api/documents`

List all uploaded documents.

### `DELETE /api/documents/{document_id}`

Delete a document and its vector embeddings.

## Chat

### `POST /api/ask-questions`

Ask a question about uploaded documents. Returns Server-Sent Events.

**Request:**
```json
{
  "message": "What are the key findings?",
  "conversation_id": null,
  "document_ids": ["uuid1", "uuid2"]
}
```

**SSE Events:**
| Event Type | Value | Description |
|------------|-------|-------------|
| `conversation_id` | string | New or existing conversation ID |
| `agent_step` | AgentStep | Real-time agent progress |
| `token` | string | Streaming response token |
| `sources` | SourceChunk[] | Source citations |
| `agent_steps` | AgentStep[] | Complete agent trace |
| `done` | null | Stream complete |
| `error` | string | Error message |

## Conversations

### `GET /api/conversations`

List all conversations (most recent first).

### `GET /api/conversations/{id}`

Get conversation with full message history.

### `POST /api/conversations`

Create a new conversation.

### `DELETE /api/conversations/{id}`

Delete a conversation and all messages.

### `GET /api/conversations/search?q={query}`

Search conversations by message content.
