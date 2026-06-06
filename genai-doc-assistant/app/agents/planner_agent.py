"""
Planner Agent — Query Decomposition
=====================================
Decomposes a user's natural language question into focused search queries
optimized for vector similarity search.

Why a separate planning step?
- User questions are often vague: "Tell me about this document"
- Vector search works better with specific, focused queries
- The planner generates 1-3 targeted search queries that cover different
  aspects of the question, improving retrieval recall

Example:
  User question: "What are the main findings and recommendations?"
  Planner output: {
    "queries": ["key findings", "recommendations and action items", "conclusions"],
    "strategy": "multi-aspect search covering findings, recommendations, and conclusions"
  }

Uses low temperature (0.3) for deterministic, consistent query generation.
Outputs structured JSON so downstream agents can parse it programmatically.
"""

import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# System prompt instructs the LLM to output ONLY valid JSON
# This structured output is essential for the pipeline — the retriever
# agent needs to parse the queries list to execute them
SYSTEM_PROMPT = """You are a planning agent in a document Q&A system.
Given a user's question and a list of available document IDs, create a retrieval strategy.

Your job is to:
1. Identify the key topics, entities, and concepts in the question
2. Generate 1-3 focused search queries to find relevant information
3. Note any specific aspects the retrieval should focus on

Respond with ONLY valid JSON in this format:
{
    "queries": ["search query 1", "search query 2"],
    "strategy": "brief description of approach",
    "focus_areas": ["key topic 1", "key topic 2"]
}"""


class PlannerAgent:
    def __init__(self) -> None:
        self._client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        self._model = f"models/{settings.GEMINI_MODEL}"

    async def plan(self, question: str, document_ids: list[str]) -> dict:
        """Generate a retrieval plan for the given question.

        Returns a dict with 'queries' (list of search strings), 'strategy', and 'focus_areas'.
        Falls back to using the raw question if JSON parsing fails.
        """
        prompt = (
            f"Question: {question}\n"
            f"Available document IDs: {', '.join(document_ids)}\n\n"
            "Create a retrieval plan."
        )

        response = await self._client.aio.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,  # Low temperature for consistent, deterministic output
                max_output_tokens=512,
            ),
        )

        # Parse JSON response, handling markdown code blocks that LLMs sometimes wrap JSON in
        text = response.text or "{}"
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Graceful fallback: if the LLM doesn't return valid JSON,
            # just use the original question as the search query
            logger.warning("planner_json_parse_failed", raw=text[:200])
            return {
                "queries": [question],
                "strategy": "direct search",
                "focus_areas": [],
            }


planner_agent = PlannerAgent()
