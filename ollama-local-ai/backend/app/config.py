"""Application configuration via pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables and/or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Ollama
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "llama3.1:8b"

    # Database
    DATABASE_PATH: str = str(
        Path(__file__).resolve().parent.parent / "data" / "ollama_local_ai.db"
    )

    # Vector store
    CHROMA_PATH: str = str(
        Path(__file__).resolve().parent.parent / "data" / "chromadb"
    )
    EMBEDDING_MODEL: str = "nomic-embed-text"

    # RAG
    CHUNK_SIZE: int = 2000
    CHUNK_OVERLAP: int = 200
    RAG_TOP_K: int = 5

    # Uploads
    UPLOAD_DIR: str = str(
        Path(__file__).resolve().parent.parent / "data" / "uploads"
    )
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB

    # CORS — origins allowed to call this API
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000


# Singleton used throughout the app
settings = Settings()
