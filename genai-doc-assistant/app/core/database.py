"""
SQLite Database Schema and Connection Management
==================================================
Uses aiosqlite for async database operations with SQLite.

Why SQLite?
- Zero configuration: no separate database server to install or manage
- File-based: the entire database is a single file (easy backup, portable)
- Suitable for single-instance deployments (Render free tier, EC2)
- Free and built into Python

Why aiosqlite?
- Wraps SQLite with async/await support so database operations don't block
  the FastAPI event loop (important when handling concurrent requests)

For scaling beyond a single server, you would migrate to PostgreSQL (via asyncpg).
"""

from pathlib import Path

import aiosqlite

from app.core.config import settings

# SQL schema defining the three core tables:
# 1. conversations - Chat session metadata (title, timestamps)
# 2. messages - Individual chat messages with optional agent traces and source citations
# 3. documents - Uploaded document metadata and processing status
SCHEMA_SQL = """
-- Conversations table: stores chat sessions
-- Each conversation has a title (auto-generated from first message) and timestamps
CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Messages table: stores individual chat messages (both user and assistant)
-- agent_steps: JSON string recording which agents ran and how long each took
-- sources: JSON string with the document chunks used to generate the response
CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    agent_steps     TEXT,
    sources         TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast lookup of messages by conversation
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

-- Documents table: tracks uploaded files and their processing status
-- status: 'processing' → 'ready' (success) or 'error' (failed)
-- collection_name: the ChromaDB collection where this document's vectors are stored
CREATE TABLE IF NOT EXISTS documents (
    id              TEXT PRIMARY KEY,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL,
    file_size       INTEGER NOT NULL DEFAULT 0,
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    collection_name TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'processing',
    uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


async def get_db() -> aiosqlite.Connection:
    """Open a new async database connection.

    Configures two important SQLite pragmas:
    - WAL (Write-Ahead Logging): allows concurrent reads while writing,
      which improves performance for a web server handling multiple requests
    - Foreign keys: enforces referential integrity (e.g., deleting a conversation
      automatically deletes its messages via ON DELETE CASCADE)
    """
    db = await aiosqlite.connect(settings.DATABASE_PATH)
    db.row_factory = aiosqlite.Row  # Access columns by name (row["id"]) instead of index
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db() -> None:
    """Create tables and ensure data directories exist.

    Called once during application startup (via the lifespan hook in main.py).
    Uses IF NOT EXISTS so it's safe to call repeatedly.
    """
    data_dir = Path(settings.DATABASE_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.CHROMA_PATH).mkdir(parents=True, exist_ok=True)

    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
    finally:
        await db.close()
