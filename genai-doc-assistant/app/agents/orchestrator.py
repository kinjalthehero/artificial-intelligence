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
        steps = []

        # Step 1: Plan
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

        # Step 2: Retrieve
        t0 = time.monotonic()
        chunks = await retriever_agent.retrieve(plan, document_ids)
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

        if not chunks:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents to answer your question.",
                "chunks": [],
                "steps": steps,
            }

        # Step 3: Reason
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

        # Step 4: Generate response
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

        # Step 5: Verify grounding
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
