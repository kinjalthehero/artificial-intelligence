from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a response generation agent in a document Q&A system.
Given an analysis of document content and source chunks, generate a clear, well-structured answer.

Rules:
- Answer ONLY from the provided information — do not add external knowledge
- Cite sources using [Source N] notation (matching the chunk numbers)
- If information is insufficient, explicitly state what is missing
- Use markdown formatting for readability (headers, lists, bold for key terms)
- Be concise but thorough"""


class ResponseAgent:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.GEMINI_MODEL}"

    async def generate(
        self, question: str, analysis: str, chunks: list[dict]
    ) -> str:
        source_summary = []
        for i, chunk in enumerate(chunks, 1):
            source_summary.append(
                f"[Source {i}]: {chunk['filename']}, page {chunk.get('page', '?')}"
            )
        sources_text = "\n".join(source_summary)

        prompt = (
            f"User Question: {question}\n\n"
            f"Analysis of Retrieved Content:\n{analysis}\n\n"
            f"Available Sources:\n{sources_text}\n\n"
            "Generate a final, well-structured answer."
        )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.5,
                max_output_tokens=4096,
            ),
        )

        return response.text or "I was unable to generate a response."


response_agent = ResponseAgent()
