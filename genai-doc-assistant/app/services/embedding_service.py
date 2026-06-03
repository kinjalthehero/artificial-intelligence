from google import genai

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.EMBEDDING_MODEL}"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        result = await self._client.aio.models.embed_content(
            model=self._model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    async def embed_single(self, text: str) -> list[float]:
        results = await self.embed([text])
        return results[0]


embedding_service = EmbeddingService()
