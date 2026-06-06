"""
Text Embedding Service (Google Gemini)
=======================================
Converts text into high-dimensional vectors (embeddings) for similarity search.

What are embeddings?
- A way to represent text as a list of numbers (a vector) that captures its meaning
- Similar texts produce similar vectors (close together in vector space)
- This enables "semantic search" — finding relevant content by meaning, not just keywords

Why Gemini embedding-001?
- 3072-dimensional vectors (high quality, captures nuanced meaning)
- Fast and cheap ($0.006 per million tokens)
- Same provider as our LLM (Gemini Flash), so one API key for everything
- Async support via google-genai SDK

The embedding flow:
  User query "What is revenue?" → [0.12, -0.45, 0.78, ...] (3072 numbers)
  Document chunk "Revenue was $5M" → [0.11, -0.44, 0.79, ...] (similar vector!)
  Cosine similarity → 0.95 (very similar = relevant chunk!)
"""

from google import genai

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class EmbeddingService:
    def __init__(self) -> None:
        # google-genai SDK client — handles authentication via API key
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.EMBEDDING_MODEL}"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Convert a batch of texts into embedding vectors.

        Returns a list of vectors, one per input text. Each vector is a list
        of 3072 floats. Uses async (.aio) to avoid blocking the event loop.
        """
        if not texts:
            return []

        result = await self._client.aio.models.embed_content(
            model=self._model,
            contents=texts,
        )
        return [e.values for e in result.embeddings]

    async def embed_single(self, text: str) -> list[float]:
        """Convenience method to embed a single text (e.g., a user query)."""
        results = await self.embed([text])
        return results[0]


embedding_service = EmbeddingService()
