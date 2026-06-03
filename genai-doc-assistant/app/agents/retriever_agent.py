from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.vector_store import vector_store

logger = get_logger(__name__)


class RetrieverAgent:
    async def retrieve(
        self, plan: dict, document_ids: list[str]
    ) -> list[dict]:
        queries = plan.get("queries", [])
        if not queries:
            return []

        all_chunks = []
        seen_ids = set()

        for query in queries:
            chunks = await vector_store.query(
                query, document_ids, settings.RAG_TOP_K
            )
            for chunk in chunks:
                chunk_key = f"{chunk['document_id']}:{chunk['chunk_index']}"
                if chunk_key not in seen_ids:
                    seen_ids.add(chunk_key)
                    all_chunks.append(chunk)

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
