"""
Application Configuration (Environment-Driven)
================================================
Uses pydantic-settings to load configuration from environment variables and .env files.

Why pydantic-settings?
- Type-safe: each setting has a defined type, validated at startup
- Environment-driven: reads from OS env vars and .env files automatically
- Single source of truth: all config in one place, not scattered across files
- No secrets in code: API keys come from environment, not hardcoded

Settings priority: OS environment variables > .env file > default values
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- Google Gemini API ---
    GOOGLE_API_KEY: str = ""  # Required: get from https://aistudio.google.com/apikey

    # LLM model for chat/reasoning (Gemini 2.5 Flash: fast, cheap, good quality)
    GEMINI_MODEL: str = "gemini-2.5-flash"
    # Embedding model for converting text to vectors (3072 dimensions)
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    # --- Storage paths ---
    DATABASE_PATH: str = str(_BASE_DIR / "data" / "genai_doc_assistant.db")  # SQLite
    CHROMA_PATH: str = str(_BASE_DIR / "data" / "chromadb")  # Vector database
    UPLOAD_DIR: str = str(_BASE_DIR / "data" / "uploads")  # Uploaded files

    # --- RAG (Retrieval-Augmented Generation) settings ---
    CHUNK_SIZE: int = 512  # Tokens per chunk (LlamaIndex SentenceSplitter)
    CHUNK_OVERLAP: int = 50  # Overlap between chunks to preserve context at boundaries
    RAG_TOP_K: int = 5  # Number of most relevant chunks to retrieve per query

    # --- Input validation limits ---
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB max file upload
    MAX_QUERY_LENGTH: int = 2000  # Max characters per question

    # --- Per-IP rate limiting (protects Gemini API from abuse) ---
    RATE_LIMIT_CHAT_PER_IP: int = 30  # Max chat queries per hour per visitor
    RATE_LIMIT_UPLOAD_PER_IP: int = 10  # Max document uploads per hour per visitor
    RATE_LIMIT_WINDOW_SECONDS: int = 3600  # Sliding window: 1 hour

    # --- CORS (Cross-Origin Resource Sharing) ---
    # These origins are allowed to call the API from a browser
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",  # React dev server (Vite)
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
    ]
    # Additional origins set via environment variable (comma-separated)
    # Example: EXTRA_CORS_ORIGINS=https://myapp.com,https://staging.myapp.com
    EXTRA_CORS_ORIGINS: str = ""

    # --- Server ---
    HOST: str = "0.0.0.0"  # Listen on all interfaces (required for Docker)
    PORT: int = 8000
    ENVIRONMENT: str = "development"  # "development" enables auto-reload


# Singleton instance used throughout the app
settings = Settings()

# Merge any extra CORS origins from environment variable into the origins list
# This allows adding production URLs (Render, EC2) without changing code
if settings.EXTRA_CORS_ORIGINS:
    for origin in settings.EXTRA_CORS_ORIGINS.split(","):
        origin = origin.strip()
        if origin and origin not in settings.CORS_ORIGINS:
            settings.CORS_ORIGINS.append(origin)
