"""
Verification Agent — Output Guardrail (Hallucination Detection)
================================================================
Checks whether the generated response is actually grounded in the source documents.

This is a safety control — even with RAG, LLMs can hallucinate (make up facts that
aren't in the documents). The verification agent acts as a final quality check:

1. Compares the answer against the source chunks
2. Identifies any claims not supported by the sources
3. Returns a grounding score (0.0 to 1.0)
4. If not grounded, a disclaimer is added to the response

Why very low temperature (0.1)?
- Verification should be deterministic and strict, not creative
- We want consistent, reproducible grounding assessments
- Higher temperature would make the verifier less reliable

Why structured JSON output?
- The orchestrator needs to programmatically check grounded=true/false
- The confidence score is displayed in the agent workflow UI
"""

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
        """Verify that the answer is grounded in the source chunks.

        Returns: {"grounded": bool, "confidence": float, "issues": list[str]}
        Falls back to grounded=True if JSON parsing fails (fail-open, not fail-closed).
        """
        # Format source chunks for comparison
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
                temperature=0.1,  # Very low: deterministic, strict verification
                max_output_tokens=512,
            ),
        )

        # Parse JSON response, handling markdown code blocks
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
