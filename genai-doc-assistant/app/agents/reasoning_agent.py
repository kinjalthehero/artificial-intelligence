from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a reasoning agent in a document Q&A system.
Given retrieved document chunks and a user question, your job is to:

1. Identify which chunks are most relevant to the question
2. Extract key facts, data points, and information
3. Note any contradictions or gaps in the information
4. Synthesize a structured analysis

Provide a clear, organized analysis that the response agent can use to generate a final answer.
Include source references using [Chunk N] notation."""


class ReasoningAgent:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.GEMINI_MODEL}"

    async def analyze(self, question: str, chunks: list[dict]) -> str:
        if not chunks:
            return "No relevant content was found in the documents."

        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Chunk {i} | {chunk['filename']}, page {chunk.get('page', '?')} | "
                f"score: {chunk['score']}]\n{chunk['content']}"
            )
        context = "\n\n".join(context_parts)

        prompt = (
            f"Question: {question}\n\n"
            f"Retrieved document chunks:\n\n{context}\n\n"
            "Analyze the above chunks and provide a structured synthesis."
        )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=2048,
            ),
        )

        return response.text or "Analysis could not be completed."


reasoning_agent = ReasoningAgent()
