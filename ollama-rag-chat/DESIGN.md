# Ollama RAG Chat - Design Document

## 1. Overview

A fully offline, locally-deployed AI chat application with document Q&A (RAG) capabilities. Runs on macOS with a double-click launcher — no internet required after initial setup.

**Target user**: Developer on a 16GB MacBook who wants a private, fast, free AI assistant for general questions and document analysis.

## 2. Goals

- **Fully offline**: Works without internet after one-time model download
- **One-click launch**: Double-click a macOS `.app` to start everything (Ollama server, FastAPI backend, React frontend)
- **Document Q&A**: Upload PDFs, text files, or markdown — ask questions answered from their content using RAG
- **Conversation history**: Persistent chat sessions stored in SQLite, browsable and searchable
- **Portfolio-ready**: Clean architecture, typed code, demonstrates RAG, embeddings, local LLM inference, full-stack skills

## 3. Architecture

```
+--------------------------------------------------+
|                  macOS Launcher                   |
|          (start.command / Automator .app)         |
+--------------------------------------------------+
         |                    |
         v                    v
+------------------+  +-------------------+
|  Ollama Server   |  |  FastAPI Backend   |
|  (port 11434)    |  |  (port 8000)       |
|                  |  |                    |
|  - llama3.1:8b   |  |  - Chat API        |
|  - nomic-embed   |  |  - RAG pipeline    |
|                  |  |  - History CRUD     |
+------------------+  |  - File upload      |
         ^            |                    |
         |            +-------------------+
         |                    |
         |                    v
         |            +-------------------+
         +------------|  ChromaDB          |
                      |  (embedded mode)   |
                      |  - doc vectors     |
                      +-------------------+
                              |
                              v
                      +-------------------+
                      |  SQLite            |
                      |  - conversations   |
                      |  - messages        |
                      |  - documents       |
                      +-------------------+

+--------------------------------------------------+
|               React Frontend                      |
|               (port 3000)                         |
|                                                   |
|  +-------------+  +---------------------------+  |
|  | Sidebar     |  | Chat Area                 |  |
|  |             |  |                           |  |
|  | History     |  | Messages (streaming)      |  |
|  | Search      |  | File upload zone          |  |
|  | New chat    |  | Input bar                 |  |
|  +-------------+  +---------------------------+  |
+--------------------------------------------------+
```

## 4. Tech Stack

| Layer      | Technology        | Why                                                    |
|------------|-------------------|--------------------------------------------------------|
| LLM        | Ollama            | Free, local, simple API, manages models                |
| Chat model | llama3.1:8b       | Best quality/speed ratio for 16GB RAM                  |
| Embeddings | nomic-embed-text  | Fast local embeddings, 768-dim, runs on Ollama         |
| Backend    | FastAPI (Python)  | Async, typed, auto-generated OpenAPI docs              |
| Vector DB  | ChromaDB          | Embedded mode (no server), persistent, Python-native   |
| Database   | SQLite            | Zero config, file-based, perfect for local app         |
| Frontend   | React + Vite      | Fast dev, modern tooling, TypeScript                   |
| Styling    | Tailwind CSS      | Rapid UI development, no custom CSS files              |
| Launcher   | Shell script + Automator | Native macOS double-click experience            |

## 5. Data Models

### 5.1 SQLite Schema

```sql
CREATE TABLE conversations (
    id          TEXT PRIMARY KEY,  -- UUID
    title       TEXT NOT NULL,     -- Auto-generated from first message
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id              TEXT PRIMARY KEY,  -- UUID
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    model           TEXT,              -- e.g. "llama3.1:8b"
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE documents (
    id              TEXT PRIMARY KEY,  -- UUID
    conversation_id TEXT REFERENCES conversations(id) ON DELETE SET NULL,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL,     -- pdf, txt, md
    chunk_count     INTEGER NOT NULL,
    collection_name TEXT NOT NULL,     -- ChromaDB collection name
    uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 5.2 ChromaDB Collections

Each uploaded document gets its own ChromaDB collection (named `doc_{document_id}`). Chunks are stored with metadata:

```python
{
    "document_id": "uuid",
    "chunk_index": 0,
    "source": "filename.pdf",
    "page": 1  # for PDFs
}
```

## 6. API Design

### 6.1 Chat Endpoints

```
POST   /api/chat                    # Send message, get streaming response
GET    /api/conversations           # List all conversations (paginated)
GET    /api/conversations/{id}      # Get conversation with messages
POST   /api/conversations           # Create new conversation
DELETE /api/conversations/{id}      # Delete conversation
GET    /api/conversations/search?q= # Full-text search across messages
```

### 6.2 Document Endpoints

```
POST   /api/documents/upload        # Upload file, chunk, embed, store
GET    /api/documents               # List uploaded documents
DELETE /api/documents/{id}          # Delete document and its vectors
```

### 6.3 System Endpoints

```
GET    /api/health                  # Backend + Ollama health check
GET    /api/models                  # List available Ollama models
```

### 6.4 Chat Request/Response

**Request:**
```json
{
    "conversation_id": "uuid-or-null",
    "message": "What does chapter 3 say about...",
    "document_ids": ["uuid"],
    "model": "llama3.1:8b"
}
```

**Response** (Server-Sent Events stream):
```
data: {"type": "conversation_id", "value": "uuid"}
data: {"type": "token", "value": "Based"}
data: {"type": "token", "value": " on"}
data: {"type": "token", "value": " the"}
...
data: {"type": "sources", "value": [{"document": "file.pdf", "page": 3, "chunk": "..."}]}
data: {"type": "done"}
```

## 7. RAG Pipeline

```
Upload flow:
  File -> Extract text -> Split into chunks (500 tokens, 50 overlap)
                       -> Embed each chunk via nomic-embed-text
                       -> Store in ChromaDB collection

Query flow:
  User question -> Embed question via nomic-embed-text
               -> Similarity search in ChromaDB (top 5 chunks)
               -> Build augmented prompt:
                    "Answer based on the following context:
                     [chunk1] [chunk2] ...
                     Question: {user_question}"
               -> Send to llama3.1:8b
               -> Stream response back with source citations
```

**Supported file types:**
- PDF (via `PyMuPDF` / `fitz`)
- Plain text (`.txt`)
- Markdown (`.md`)

**Chunking strategy:** Fixed-size with overlap. 500 tokens per chunk, 50 token overlap. Good balance between context and retrieval precision.

## 8. Frontend Design

### 8.1 Layout

```
+-------+------------------------------------------+
|       |  Ollama RAG Chat            [model: v]   |
| NEW   |------------------------------------------|
| CHAT  |                                          |
|       |  [User message bubble]                   |
| ---   |                                          |
|       |  [Assistant response bubble]             |
| Recent|  [Source: file.pdf, page 3]              |
| Chats |                                          |
|       |  [User message bubble]                   |
| > Ch1 |                                          |
| > Ch2 |  [Assistant response streaming...]       |
| > Ch3 |                                          |
|       |------------------------------------------|
| ---   |                                          |
|       |  [Drop files here or click to upload]    |
| Search|  [attached: report.pdf x]                |
| [___] |                                          |
|       |  [Type your message...        ] [Send]   |
+-------+------------------------------------------+
```

### 8.2 Key UI Features

- **Streaming responses**: Tokens appear as they're generated (SSE)
- **Drag-and-drop file upload**: Visual drop zone, shows processing progress
- **Conversation sidebar**: Sorted by recency, searchable, deletable
- **Source citations**: Expandable cards showing which document chunks informed the answer
- **Dark/light theme**: Toggle, persisted in localStorage
- **Responsive**: Works well at different window sizes
- **Loading states**: Skeleton loaders while Ollama processes

### 8.3 Component Tree

```
App
├── Sidebar
│   ├── NewChatButton
│   ├── ConversationList
│   │   └── ConversationItem (x N)
│   └── SearchBar
├── ChatArea
│   ├── ChatHeader (model selector)
│   ├── MessageList
│   │   ├── MessageBubble (user)
│   │   └── MessageBubble (assistant)
│   │       └── SourceCitation (expandable)
│   ├── FileUploadZone
│   └── MessageInput
└── ThemeToggle
```

## 9. Project Structure

```
ollama-rag-chat/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, lifespan
│   │   ├── config.py            # Settings (ports, paths, model names)
│   │   ├── database.py          # SQLite connection, schema init
│   │   ├── models.py            # Pydantic request/response models
│   │   ├── routers/
│   │   │   ├── chat.py          # Chat + streaming endpoints
│   │   │   ├── conversations.py # CRUD for conversations
│   │   │   ├── documents.py     # Upload, list, delete docs
│   │   │   └── system.py        # Health check, model list
│   │   ├── services/
│   │   │   ├── ollama_service.py    # Ollama API wrapper
│   │   │   ├── rag_service.py       # Chunking, embedding, retrieval
│   │   │   └── document_parser.py   # PDF/text extraction
│   │   └── vector_store.py      # ChromaDB wrapper
│   ├── data/                    # SQLite DB + ChromaDB files (gitignored)
│   ├── requirements.txt
│   └── tests/
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Sidebar/
│   │   │   ├── Chat/
│   │   │   └── Upload/
│   │   ├── hooks/
│   │   │   ├── useChat.ts       # SSE streaming logic
│   │   │   ├── useConversations.ts
│   │   │   └── useDocuments.ts
│   │   ├── api/
│   │   │   └── client.ts        # Typed API client
│   │   └── types/
│   │       └── index.ts
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── scripts/
│   ├── start.sh                 # Launch script (Ollama + backend + frontend)
│   ├── setup.sh                 # One-time setup (install deps, pull models)
│   └── OllamaRAGChat.app/      # macOS Automator app wrapper
├── DESIGN.md
├── README.md (created during implementation)
└── .gitignore
```

## 10. macOS Launcher

### 10.1 start.sh

```bash
#!/bin/bash
# Start Ollama if not running
pgrep -x "ollama" > /dev/null || open -a Ollama

# Wait for Ollama to be ready
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do sleep 1; done

# Start FastAPI backend
cd backend && source venv/bin/activate
uvicorn app.main:app --port 8000 &
BACKEND_PID=$!

# Start React frontend
cd ../frontend && npm run preview -- --port 3000 &
FRONTEND_PID=$!

# Open browser
sleep 2 && open http://localhost:3000

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

### 10.2 Double-Click App

Use macOS Automator to create an Application that runs `start.sh`. This produces a `.app` bundle the user can:
- Double-click from Finder
- Keep in the Dock
- Add to Login Items for auto-start

### 10.3 setup.sh (One-Time)

```bash
#!/bin/bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull nomic-embed-text

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd ../frontend
npm install
npm run build
```

## 11. Implementation Plan

### Phase 1: Foundation (Backend + Basic Chat)
1. FastAPI project setup with config, database, models
2. Ollama service — chat completion with streaming
3. Conversation CRUD endpoints
4. Message persistence to SQLite
5. Health check and model listing endpoints
6. **Milestone**: Can chat via Swagger UI at `/docs`

### Phase 2: RAG Pipeline
1. Document parser (PDF, text, markdown)
2. Text chunking service
3. ChromaDB integration — embed and store chunks
4. Retrieval — similarity search on user query
5. Augmented prompt construction with retrieved context
6. Source citation extraction in responses
7. Document upload/list/delete endpoints
8. **Milestone**: Can upload a PDF and ask questions about it via API

### Phase 3: React Frontend
1. Vite + React + TypeScript + Tailwind setup
2. Chat interface with streaming (SSE)
3. Conversation sidebar with history
4. File upload with drag-and-drop
5. Source citation display
6. Search across conversations
7. Dark/light theme
8. **Milestone**: Full working UI

### Phase 4: Packaging & Polish
1. `start.sh` launcher script
2. `setup.sh` one-time installer
3. macOS Automator `.app` bundle
4. Error handling (Ollama not running, model not pulled)
5. Loading states, empty states, error toasts
6. **Milestone**: Double-click to launch, ready to demo

## 12. Recruiter Talking Points

This project demonstrates:
- **Local LLM inference** — understanding of model sizes, quantization, hardware constraints
- **RAG pipeline** — document parsing, chunking strategies, vector embeddings, similarity search
- **Full-stack development** — React + TypeScript frontend, Python + FastAPI backend
- **Streaming architecture** — Server-Sent Events for real-time token delivery
- **Data persistence** — SQLite for structured data, ChromaDB for vector data
- **Developer experience** — one-click launcher, clean project structure
- **Privacy-first design** — everything runs locally, no data leaves the machine
