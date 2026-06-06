"""
Agent Orchestrator — 5-Step Sequential Pipeline
=================================================
Coordinates the multi-agent reasoning pipeline for document Q&A.

Pipeline: Planner → Retriever → Reasoning → Response → Verification

Why 5 separate agents instead of one LLM call?
- Separation of concerns: each agent has a focused role with a specific system prompt
- Better results: planning retrieval queries separately improves search quality
- Transparency: each step is timed and shown in the UI (AgentWorkflow component)
- Debugging: if an answer is wrong, you can see which step went wrong
- Guardrails: the verification agent catches hallucinations before they reach the user

Why sequential (not parallel)?
- Each step depends on the output of the previous step:
  Plan → (queries) → Retrieve → (chunks) → Reason → (analysis) → Respond → (answer) → Verify

The pipeline makes ~5 Gemini API calls per query (~15-20 seconds total).
If the pipeline fails (e.g., rate limit), the chat router falls back to direct RAG.
"""

import time

from app.agents.planner_agent import planner_agent
from app.agents.retriever_agent import retriever_agent
from app.agents.reasoning_agent import reasoning_agent
from app.agents.response_agent import response_agent
from app.agents.verification_agent import verification_agent
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AgentOrchestrator:
    async def process_query(
        self,
        question: str,
        document_ids: list[str],
        initial_chunks: list[dict] | None = None,
    ) -> dict:
        """Run the full 5-agent pipeline and return the answer with metadata.

        Returns a dict with:
        - answer: the final response text
        - chunks: the retrieved document chunks (for source citations)
        - steps: list of AgentStep dicts (for the UI progress bar)
        - verification: grounding check result
        """
        steps = []

        # Step 1: PLANNER — Decompose the user's question into focused search queries
        # Instead of searching with the raw question (which may be vague), the planner
        # generates 1-3 specific queries optimized for vector search
        t0 = time.monotonic()
        plan = await planner_agent.plan(question, document_ids)
        duration = int((time.monotonic() - t0) * 1000)
        steps.append({
            "agent": "planner",
            "action": "Decomposed query into retrieval strategy",
            "result": f"Generated {len(plan.get('queries', []))} search queries",
            "duration_ms": duration,
        })
        logger.info("agent_step_planner", duration_ms=duration, queries=plan.get("queries", []))

        # Step 2: RETRIEVER — Execute the planned queries against the vector store
        # Searches across all selected documents, deduplicates overlapping results,
        # and ranks by relevance score
        t0 = time.monotonic()
        chunks = await retriever_agent.retrieve(plan, document_ids)
        # Fallback: if retriever found nothing, use the initial chunks from the RAG service
        if not chunks and initial_chunks:
            chunks = initial_chunks
        duration = int((time.monotonic() - t0) * 1000)
        steps.append({
            "agent": "retriever",
            "action": f"Searched knowledge base across {len(document_ids)} document(s)",
            "result": f"Found {len(chunks)} relevant chunks",
            "duration_ms": duration,
        })
        logger.info("agent_step_retriever", duration_ms=duration, chunks_found=len(chunks))

        # Early exit if no relevant content was found
        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "chunks": [],
                "steps": steps,
            }

        # Step 3: REASONING — Analyze the retrieved chunks to identify key facts,
        # contradictions, and gaps. This step synthesizes raw chunks into a structured
        # analysis that's easier for the response agent to work with.
        t0 = time.monotonic()
        analysis = await reasoning_agent.analyze(question, chunks)
        duration = int((time.monotonic() - t0) * 1000)
        steps.append({
            "agent": "reasoning",
            "action": "Analyzed and synthesized retrieved content",
            "result": f"Analysis complete ({len(analysis)} chars)",
            "duration_ms": duration,
        })
        logger.info("agent_step_reasoning", duration_ms=duration)

        # Step 4: RESPONSE — Generate the final user-facing answer with [Source N] citations
        # Uses the analysis (not raw chunks) for better coherence, but has access to
        # source metadata for accurate citations
        t0 = time.monotonic()
        answer = await response_agent.generate(question, analysis, chunks)
        duration = int((time.monotonic() - t0) * 1000)
        steps.append({
            "agent": "response",
            "action": "Generated grounded answer with citations",
            "result": f"Response generated ({len(answer)} chars)",
            "duration_ms": duration,
        })
        logger.info("agent_step_response", duration_ms=duration)

        # Step 5: VERIFICATION — Output guardrail that checks if the response
        # is actually grounded in the source documents. Catches hallucinations
        # before they reach the user. Returns a confidence score (0.0 to 1.0).
        t0 = time.monotonic()
        verification = await verification_agent.verify(answer, chunks)
        duration = int((time.monotonic() - t0) * 1000)
        grounded = verification.get("grounded", True)
        confidence = verification.get("confidence", 0.5)
        steps.append({
            "agent": "verification",
            "action": "Verified response grounding",
            "result": f"Grounded: {grounded}, Confidence: {confidence:.0%}",
            "duration_ms": duration,
        })
        logger.info(
            "agent_step_verification",
            duration_ms=duration,
            grounded=grounded,
            confidence=confidence,
        )

        # If verification fails, add a disclaimer to the response
        # rather than blocking it entirely (the answer may still be partially useful)
        if not grounded:
            issues = verification.get("issues", [])
            disclaimer = "\n\n---\n*Note: Some claims in this response may not be fully supported by the source documents.*"
            if issues:
                disclaimer += "\n*Issues: " + "; ".join(issues) + "*"
            answer += disclaimer

        return {
            "answer": answer,
            "chunks": chunks,
            "steps": steps,
            "verification": verification,
        }


orchestrator = AgentOrchestrator()
