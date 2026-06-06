"""
RAG (Retrieval-Augmented Generation) Service
==============================================
Orchestrates the RAG pipeline: retrieve relevant chunks → build augmented prompt.

What is RAG?
- Instead of asking the LLM to answer from its training data (which may be outdated
  or wrong), we first RETRIEVE relevant chunks from the user's documents, then
  AUGMENT the prompt with that context, and finally let the LLM GENERATE an answer
  based only on the provided context.
- This grounds the LLM's response in actual document content, reducing hallucination.

The RAG flow:
  User question → Embed question → Search ChromaDB → Get top-K chunks
  → Build prompt with context → Send to Gemini → Get grounded answer

This service is used as a fallback when the agent pipeline fails (e.g., rate limit).
The agent pipeline (orchestrator.py) provides a more sophisticated version of this
with planning, reasoning, and verification steps.
"""

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.vector_store import vector_store

logger = get_logger(__name__)

# System prompt that instructs the LLM to ONLY answer from the provided context.
# This is the key to preventing hallucination in RAG — the LLM is told to say
# "I don't have enough information" rather than making things up.
GROUNDING_PROMPT = (
    "You are a document analysis assistant. Answer ONLY based on the provided context.\n"
    "If the context does not contain enough information, say "
    '"I don\'t have enough information in the uploaded documents to answer this question."\n'
    "Do NOT include [Source N] citations in your answer — sources are shown separately.\n"
    "Do not use any knowledge outside of the provided context.\n"
    "Use markdown formatting for readability."
)


class RAGService:
    async def retrieve(
        self, question: str, document_ids: list[str], top_k: int | None = None
    ) -> list[dict]:
        """Retrieve the most relevant document chunks for a question."""
        top_k = top_k or settings.RAG_TOP_K
        return await vector_store.query(question, document_ids, top_k)

    def build_context(self, chunks: list[dict]) -> str:
        """Format retrieved chunks into a labeled context block.

        Each chunk is labeled [Source N: filename, page X] so the LLM can
        reference specific sources in its answer using [Source N] notation.
        """
        if not chunks:
            return ""

        parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["filename"]
            page = chunk.get("page", "?")
            parts.append(f"[Source {i}: {source}, page {page}]\n{chunk['content']}")

        return "\n\n".join(parts)

    def build_rag_prompt(self, question: str, chunks: list[dict]) -> str:
        """Build the full augmented prompt: context block + user question.

        The --- CONTEXT --- delimiters help the LLM distinguish between
        the reference material and the actual question.
        """
        context = self.build_context(chunks)
        return (
            f"--- CONTEXT ---\n{context}\n--- END CONTEXT ---\n\n"
            f"Question: {question}"
        )

    def get_system_prompt(self) -> str:
        """Return the grounding system prompt for RAG responses."""
        return GROUNDING_PROMPT


rag_service = RAGService()
