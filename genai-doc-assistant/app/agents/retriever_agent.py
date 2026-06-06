"""
Retriever Agent — Vector Search Execution
===========================================
Executes the planned search queries against the ChromaDB vector store
and returns deduplicated, ranked results.

Why a separate retriever (vs. searching directly in the orchestrator)?
- Handles multi-query deduplication: when the planner generates 3 queries,
  they may return overlapping chunks. The retriever deduplicates by chunk ID.
- Aggregates results across multiple documents and queries
- Returns more chunks than a single query would (top_k * 2) to give the
  reasoning agent a broader context to work with

This agent doesn't use the LLM — it's pure vector search logic.
"""

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.vector_store import vector_store

logger = get_logger(__name__)


class RetrieverAgent:
    async def retrieve(
        self, plan: dict, document_ids: list[str]
    ) -> list[dict]:
        """Execute all planned queries and return deduplicated, ranked chunks.

        Process:
        1. Extract search queries from the planner's output
        2. Run each query against the vector store
        3. Deduplicate: if multiple queries return the same chunk, keep it once
           (tracked by document_id + chunk_index composite key)
        4. Sort all results by relevance score (highest first)
        5. Return up to 2x top_k chunks (more context for the reasoning agent)
        """
        queries = plan.get("queries", [])
        if not queries:
            return []

        all_chunks = []
        seen_ids = set()  # Track seen chunks to prevent duplicates

        for query in queries:
            chunks = await vector_store.query(
                query, document_ids, settings.RAG_TOP_K
            )
            for chunk in chunks:
                # Deduplicate by document + chunk index combination
                chunk_key = f"{chunk['document_id']}:{chunk['chunk_index']}"
                if chunk_key not in seen_ids:
                    seen_ids.add(chunk_key)
                    all_chunks.append(chunk)

        # Sort by relevance score and cap at 2x top_k
        all_chunks.sort(key=lambda x: x["score"], reverse=True)
        max_chunks = settings.RAG_TOP_K * 2
        result = all_chunks[:max_chunks]

        logger.info(
            "retriever_complete",
            queries=len(queries),
            total_found=len(all_chunks),
            returned=len(result),
        )
        return result


retriever_agent = RetrieverAgent()
