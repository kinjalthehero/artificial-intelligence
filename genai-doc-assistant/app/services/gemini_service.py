"""
Google Gemini LLM Service
==========================
Handles all direct communication with the Google Gemini API.

Why Gemini 2.5 Flash?
- Fast: optimized for low latency (important for interactive chat)
- Cheap: ~$0.15/1M input tokens, $0.60/1M output tokens
- High quality: strong reasoning and instruction following
- Free tier available: 15 RPM for development/testing

Uses the google-genai SDK (official Google AI SDK):
- Async support (.aio) for non-blocking API calls
- Streaming support for token-by-token response delivery
- Simple API key authentication (no OAuth complexity)

Two modes of operation:
1. stream_chat: Used for direct chat responses (SSE streaming to frontend)
2. generate: Used by agents for non-streaming LLM calls (planning, reasoning, etc.)
"""

from typing import AsyncGenerator

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class GeminiService:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.GEMINI_MODEL}"

    async def is_healthy(self) -> bool:
        """Check if the Gemini API is reachable by sending a minimal request.

        Called by the /api/health-check endpoint. The frontend uses this to show
        "Gemini Connected" (green) or "Gemini Offline" (red) status badge.
        """
        try:
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents="Hi",
                config=types.GenerateContentConfig(max_output_tokens=5),
            )
            return response.text is not None
        except Exception as e:
            logger.warning("gemini_health_check_failed", error=str(e))
            return False

    async def stream_chat(
        self,
        system_prompt: str,
        messages: list[dict],
    ) -> AsyncGenerator[str, None]:
        """Stream a chat response token-by-token from Gemini.

        This is an async generator — it yields text chunks as they arrive from the API.
        The chat router sends each chunk as an SSE (Server-Sent Event) to the frontend,
        creating the real-time typing effect.

        Messages are converted to Gemini's Content format:
        - role "user" → Gemini role "user"
        - role "assistant" → Gemini role "model"
        """
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,  # Moderate creativity for natural responses
            max_output_tokens=4096,
        )

        # generate_content_stream returns a coroutine that resolves to an async iterator
        # Must be awaited first, then iterated with 'async for'
        response = await self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=contents,
            config=config,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate a complete (non-streaming) response from Gemini.

        Used by agents for planning, reasoning, and verification — where we need
        the full response before proceeding to the next step.
        Lower temperature (0.3) for more deterministic, focused outputs.
        """
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=4096,
        )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=user_prompt,
            config=config,
        )
        return response.text or ""


gemini_service = GeminiService()
