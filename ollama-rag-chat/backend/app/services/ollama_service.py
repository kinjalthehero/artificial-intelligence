"""Wrapper around the ollama Python library for chat, model listing, and health checks."""

from typing import AsyncGenerator

from ollama import AsyncClient

from app.config import settings


class OllamaService:
    """Async interface to the Ollama server."""

    def __init__(self, host: str | None = None) -> None:
        self._host = host or settings.OLLAMA_HOST
        self._client = AsyncClient(host=self._host)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def is_healthy(self) -> bool:
        """Return True if the Ollama server is reachable."""
        try:
            await self._client.list()
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Models
    # ------------------------------------------------------------------

    async def list_models(self) -> list[dict]:
        """Return the list of locally available models.

        Each dict contains at least ``name``; may also have ``size`` and
        ``modified_at`` depending on the Ollama version.
        """
        response = await self._client.list()
        models = []
        for m in response.models:
            models.append(
                {
                    "name": getattr(m, "model", "") or getattr(m, "name", ""),
                    "size": getattr(m, "size", None),
                    "modified_at": str(getattr(m, "modified_at", "")),
                }
            )
        return models

    # ------------------------------------------------------------------
    # Chat (streaming)
    # ------------------------------------------------------------------

    async def stream_chat(
        self,
        messages: list[dict],
        model: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Yield tokens from an Ollama chat completion.

        ``messages`` should follow the Ollama/OpenAI format::

            [{"role": "user", "content": "Hello"}]

        Each yielded string is a single token fragment.
        """
        model = model or settings.DEFAULT_MODEL

        stream = await self._client.chat(
            model=model,
            messages=messages,
            stream=True,
        )

        async for chunk in stream:
            token = chunk.message.content if chunk.message else ""
            if token:
                yield token


# Module-level singleton so routers can import directly.
ollama_service = OllamaService()
