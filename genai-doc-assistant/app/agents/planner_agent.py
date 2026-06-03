import json

from google import genai
from google.genai import types

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)

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
                temperature=0.3,
                max_output_tokens=512,
            ),
        )

        text = response.text or "{}"
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            text = text.rsplit("```", 1)[0]

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("planner_json_parse_failed", raw=text[:200])
            return {
                "queries": [question],
                "strategy": "direct search",
                "focus_areas": [],
            }


planner_agent = PlannerAgent()
