"""
Reasoning Agent — Content Analysis and Synthesis
==================================================
Analyzes retrieved document chunks to extract key facts, identify relevance,
and synthesize a structured analysis for the response agent.

Why separate reasoning from response generation?
- Analysis vs. presentation: the reasoning agent focuses on UNDERSTANDING the content,
  while the response agent focuses on PRESENTING it clearly to the user
- Better quality: two-step process (analyze then respond) produces more thorough,
  accurate answers than trying to do both in one LLM call
- Transparency: the analysis can be logged/inspected for debugging

The reasoning agent receives the raw chunks with their relevance scores and
produces a structured summary that the response agent can work with.
"""

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
        """Analyze retrieved chunks and produce a structured synthesis.

        Each chunk is labeled with its source file, page number, and relevance score
        so the reasoning agent can weigh more relevant chunks higher.
        """
        if not chunks:
            return "No relevant content was found in the documents."

        # Format chunks with metadata for the LLM
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
                temperature=0.3,  # Low temperature for factual analysis
                max_output_tokens=2048,
            ),
        )

        return response.text or "Analysis could not be completed."


reasoning_agent = ReasoningAgent()
