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
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=4096,
        )

        async for chunk in self._client.aio.models.generate_content_stream(
            model=self._model,
            contents=contents,
            config=config,
        ):
            if chunk.text:
                yield chunk.text

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
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
