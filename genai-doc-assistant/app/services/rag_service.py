from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.vector_store import vector_store

logger = get_logger(__name__)

GROUNDING_PROMPT = (
    "You are a document analysis assistant. Answer ONLY based on the provided context.\n"
    "If the context does not contain enough information, say "
    '"I don\'t have enough information in the uploaded documents to answer this question."\n'
    "Always cite sources using [Source N] notation.\n"
    "Do not use any knowledge outside of the provided context.\n"
    "Use markdown formatting for readability."
)


class RAGService:
    async def retrieve(
        self, question: str, document_ids: list[str], top_k: int | None = None
    ) -> list[dict]:
        top_k = top_k or settings.RAG_TOP_K
        return await vector_store.query(question, document_ids, top_k)

    def build_context(self, chunks: list[dict]) -> str:
        if not chunks:
            return ""

        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["filename"]
            page = chunk.get("page", "?")
            parts.append(f"[Source {i}: {source}, page {page}]\n{chunk['content']}")

        return "\n\n".join(parts)

    def build_rag_prompt(self, question: str, chunks: list[dict]) -> str:
        context = self.build_context(chunks)
        return (
            f"--- CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
            f"Question: {question}"
        )

    def get_system_prompt(self) -> str:
        return GROUNDING_PROMPT


rag_service = RAGService()
