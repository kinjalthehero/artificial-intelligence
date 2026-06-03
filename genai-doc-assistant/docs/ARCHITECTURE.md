# System Architecture

**Live Demo**: https://genai-doc-assistant-slnu.onrender.com

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                      │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌───────────┐  │
│  │ Chat UI  │  │ Document  │  │ Sidebar  │  │  Agent    │  │
│  │ (SSE)    │  │ Upload    │  │          │  │ Workflow  │  │
│  └────┬─────┘  └─────┬─────┘  └──────────┘  └───────────┘  │
│       │              │                                        │
└───────┼──────────────┼────────────────────────────────────────┘
        │  HTTP/SSE    │  Multipart
        ▼              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                             │
│                                                               │
│  ┌─────────────────── API Layer ──────────────────────────┐  │
│  │ /api/ask-questions  /api/upload-document  /api/health   │  │
│  │ /api/documents      /api/conversations                  │  │
│  └─────────────┬───────────────┬──────────────────────────┘  │
│                │               │                              │
│  ┌─────────────▼───────┐  ┌───▼──────────────────────────┐  │
│  │   Agent Pipeline    │  │    Document Pipeline          │  │
│  │                     │  │                               │  │
│  │  ┌───────────┐     │  │  ┌──────────┐ ┌───────────┐  │  │
│  │  │ Planner   │     │  │  │ Parser   │ │ Chunking  │  │  │
│  │  └─────┬─────┘     │  │  │ (6 fmt)  │ │ (LlamaIdx)│  │  │
│  │  ┌─────▼─────┐     │  │  └────┬─────┘ └─────┬─────┘  │  │
│  │  │ Retriever │     │  │       │              │        │  │
│  │  └─────┬─────┘     │  │  ┌────▼──────────────▼─────┐  │  │
│  │  ┌─────▼─────┐     │  │  │     Embedding Service   │  │  │
│  │  │ Reasoning │     │  │  │  (Gemini embedding-001) │  │  │
│  │  └─────┬─────┘     │  │  └───────────┬─────────────┘  │  │
│  │  ┌─────▼─────┐     │  │              │                │  │
│  │  │ Response  │     │  │  ┌───────────▼─────────────┐  │  │
│  │  └─────┬─────┘     │  │  │      ChromaDB           │  │  │
│  │  ┌─────▼─────┐     │  │  │  (Vector Store)         │  │  │
│  │  │ Verifier  │     │  │  └─────────────────────────┘  │  │
│  │  └───────────┘     │  └───────────────────────────────┘  │
│  └─────────────────────┘                                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   SQLite     │  │  Rate        │  │  Structured      │   │
│  │  (History)   │  │  Limiter     │  │  Logging         │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │  Google Gemini API    │
              │  (2.5 Flash, Free)    │
              └───────────────────────┘
```

## Data Flow

### Document Upload Flow
```
File Upload → Validate (type, size) → Extract Text → Chunk (SentenceSplitter)
→ Embed (Gemini) → Store in ChromaDB → Record metadata in SQLite
```

### Query Flow (with Agents)
```
User Question → Validate → Planner Agent (creates strategy)
→ Retriever Agent (vector search) → Reasoning Agent (analyze)
→ Response Agent (generate answer) → Verification Agent (check grounding)
→ Stream response via SSE
```

## Database Schema

- **conversations**: id, title, created_at, updated_at
- **messages**: id, conversation_id, role, content, agent_steps (JSON), sources (JSON)
- **documents**: id, filename, file_type, file_size, chunk_count, collection_name, status
