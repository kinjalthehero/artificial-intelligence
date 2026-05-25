"""SQLite database connection and schema initialization using aiosqlite."""

from pathlib import Path

import aiosqlite

from app.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS conversations (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    model           TEXT,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_messages_conversation_id
    ON messages(conversation_id);

CREATE INDEX IF NOT EXISTS idx_messages_content
    ON messages(content);

CREATE TABLE IF NOT EXISTS documents (
    id              TEXT PRIMARY KEY,
    conversation_id TEXT REFERENCES conversations(id) ON DELETE SET NULL,
    filename        TEXT NOT NULL,
    file_type       TEXT NOT NULL,
    chunk_count     INTEGER NOT NULL DEFAULT 0,
    collection_name TEXT NOT NULL,
    uploaded_at     DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_documents_conversation_id
    ON documents(conversation_id);
"""


async def get_db() -> aiosqlite.Connection:
    """Open a new database connection.

    The caller is responsible for closing it (use ``async with`` or call
    ``await db.close()`` in a finally block).
    """
    db = await aiosqlite.connect(settings.DATABASE_PATH)
    # Return rows as sqlite3.Row so we can access columns by name.
    db.row_factory = aiosqlite.Row
    # Enable WAL mode for better concurrent read performance.
    await db.execute("PRAGMA journal_mode=WAL")
    # Enable foreign-key enforcement (off by default in SQLite).
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db() -> None:
    """Create tables and indexes if they don't exist.

    Called once during application startup (lifespan).
    """
    # Ensure the data directory exists.
    data_dir = Path(settings.DATABASE_PATH).parent
    data_dir.mkdir(parents=True, exist_ok=True)

    db = await get_db()
    try:
        await db.executescript(SCHEMA_SQL)
        await db.commit()
    finally:
        await db.close()
