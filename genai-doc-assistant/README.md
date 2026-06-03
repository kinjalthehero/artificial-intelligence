# GenAI Document Assistant

AI-powered document Q&A application with RAG pipeline and multi-agent reasoning.

Upload documents (PDF, TXT, CSV, Excel, JSON, YAML), ask natural language questions, and get accurate, grounded answers with source citations — powered by a 5-agent reasoning pipeline.

## Architecture

```
User → React Frontend → FastAPI Backend → Agent Pipeline → Gemini 2.5 Flash
                                              │
                              ┌────────────────┼────────────────┐
                              ▼                ▼                ▼
                          Planner →     Retriever →      Reasoning →
                                                                │
                                                    Response → Verify
                                                                │
                              ChromaDB ◄────────────────────────┘
                           (Vector Store)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, TypeScript, Vite, Tailwind CSS 4 |
| Backend | FastAPI, Python 3.11 |
| LLM | Google Gemini 2.5 Flash (free tier) |
| Embeddings | Gemini embedding-001 |
| Vector Store | ChromaDB (persistent) |
| Agents | LlamaIndex |
| Database | SQLite (async) |
| Deployment | Docker, Render.com |

## Features

- **6 Document Formats**: Upload PDF, TXT, CSV, Excel, JSON, and YAML files
- **Multi-Agent Reasoning**: 5-agent pipeline (Planner, Retriever, Reasoning, Response, Verification)
- **Real-Time Streaming**: Server-Sent Events for token-by-token response delivery
- **Agent Workflow Visualization**: See each agent's progress, timing, and results in the UI
- **Source Citations**: Every answer includes [Source N] references to specific document chunks
- **Output Verification**: Dedicated verification agent checks response grounding
- **Dark/Light Theme**: Toggle between themes
- **Conversation History**: Full chat history with search

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Google API Key ([Get one free](https://aistudio.google.com/apikey))

### Setup

```bash
# Clone and navigate
cd genai-doc-assistant

# Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..

# Environment
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Run Locally

```bash
# Terminal 1: Backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend (dev mode)
cd frontend
npm run dev
```

Open http://localhost:3000

### Run with Docker

```bash
docker build -t genai-doc-assistant .
docker run -p 8000:8000 -e GOOGLE_API_KEY=your-key genai-doc-assistant
```

Open http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health-check` | System health status |
| POST | `/api/upload-document` | Upload and process a document |
| GET | `/api/documents` | List uploaded documents |
| DELETE | `/api/documents/{id}` | Delete a document |
| POST | `/api/ask-questions` | Ask a question (SSE streaming) |
| GET | `/api/conversations` | List conversations |
| GET | `/api/conversations/{id}` | Get conversation with messages |
| POST | `/api/conversations` | Create conversation |
| DELETE | `/api/conversations/{id}` | Delete conversation |

## Project Structure

```
genai-doc-assistant/
├── app/
│   ├── api/          # FastAPI route handlers
│   ├── services/     # Document parsing, chunking, embedding, RAG
│   ├── agents/       # LlamaIndex agent pipeline (5 agents)
│   ├── core/         # Config, database, models, logging
│   └── utils/        # Validators, rate limiter, text cleaner
├── frontend/         # React 19 + TypeScript + Tailwind
├── data/sample/      # Sample documents for demo
├── docs/             # Architecture, API, agent workflow docs
├── main.py           # FastAPI entry point
├── Dockerfile        # Multi-stage Docker build
└── render.yaml       # Render.com deployment blueprint
```

## Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [Agent Workflow](docs/AGENT_WORKFLOW.md)
- [API Reference](docs/API_REFERENCE.md)
- [Limitations & Security](docs/LIMITATIONS.md)

## Deployment

Deploy to Render.com (free tier):

1. Push to GitHub
2. Connect repo to Render.com
3. Set `GOOGLE_API_KEY` environment variable
4. Deploy (auto-detects Dockerfile)

See [Deployment Guide](docs/LIMITATIONS.md) for details.

## License

MIT
