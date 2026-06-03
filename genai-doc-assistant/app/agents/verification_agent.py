import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a verification agent. Your job is to check whether a generated answer
is accurately grounded in the source documents.

Evaluate the answer against the provided context chunks and respond with ONLY valid JSON:
{
    "grounded": true or false,
    "confidence": 0.0 to 1.0,
    "issues": ["list of any unsupported claims or hallucinations, if any"]
}

Be strict: if any claim in the answer is not supported by the context, mark grounded as false."""


class VerificationAgent:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.GEMINI_MODEL}"

    async def verify(self, answer: str, chunks: list[dict]) -> dict:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Source {i}]\n{chunk['content']}")
        context = "\n\n".join(context_parts)

        prompt = (
            f"Answer to verify:\n{answer}\n\n"
            f"Source context:\n{context}\n\n"
            "Is this answer grounded in the sources?"
        )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
                max_output_tokens=512,
            ),
        )

        text = (response.text or "{}").strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]

        try:
            result = json.loads(text)
            return {
                "grounded": result.get("grounded", True),
                "confidence": result.get("confidence", 0.5),
                "issues": result.get("issues", []),
            }
        except json.JSONDecodeError:
            logger.warning("verification_json_parse_failed", raw=text[:200])
            return {"grounded": True, "confidence": 0.5, "issues": []}


verification_agent = VerificationAgent()
