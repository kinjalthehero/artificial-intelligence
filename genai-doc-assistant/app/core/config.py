from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    GOOGLE_API_KEY: str = ""

    GEMINI_MODEL: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "gemini-embedding-001"

    DATABASE_PATH: str = str(_BASE_DIR / "data" / "genai_doc_assistant.db")
    CHROMA_PATH: str = str(_BASE_DIR / "data" / "chromadb")
    UPLOAD_DIR: str = str(_BASE_DIR / "data" / "uploads")

    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    RAG_TOP_K: int = 5

    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10 MB
    MAX_QUERY_LENGTH: int = 2000

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"


settings = Settings()
