"""
LlamaIndex Agent Tools
========================
Defines tools that LlamaIndex agents can use via function calling.

What is a FunctionTool?
- LlamaIndex's way of giving agents the ability to call external functions
- The agent sees the tool's name and description, then decides when to call it
- When called, the function executes and returns results to the agent

In our pipeline, the retriever agent uses the search_knowledge_base tool
to query the ChromaDB vector store. This bridges the LLM agent world
(LlamaIndex) with our vector database (ChromaDB).

Note: Currently the retriever agent calls vector_store.query() directly
instead of through this tool, but the tool is available for future use
with LlamaIndex's ReActAgent or FunctionCallingAgent patterns.
"""

import asyncio

from llama_index.core.tools import FunctionTool

from app.services.vector_store import vector_store


def search_knowledge_base(query: str, document_ids_csv: str, top_k: int = 5) -> str:
    """Search the vector store for chunks relevant to a query.

    This is a synchronous wrapper around the async vector_store.query() method,
    needed because LlamaIndex tools expect synchronous functions.

    Args:
        query: The search query text
        document_ids_csv: Comma-separated document IDs to search across
        top_k: Number of top results to return (default: 5)

    Returns:
        Formatted string with chunk content, source info, and relevance scores
    """
    doc_ids = [d.strip() for d in document_ids_csv.split(",") if d.strip()]
    if not doc_ids:
        return "No document IDs provided."

    # Bridge async to sync for LlamaIndex compatibility
    chunks = asyncio.get_event_loop().run_until_complete(
        vector_store.query(query, doc_ids, top_k)
    )

    if not chunks:
        return "No relevant content found."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Chunk {i} | {chunk['filename']}, page {chunk.get('page', '?')} | "
            f"score: {chunk['score']}]\n{chunk['content']}"
        )
    return "\n\n".join(parts)


# Register as a LlamaIndex FunctionTool so agents can discover and call it
search_tool = FunctionTool.from_defaults(
    fn=search_knowledge_base,
    name="search_knowledge_base",
    description=(
        "Search the vector knowledge base for document chunks relevant to a query. "
        "Parameters: query (str), document_ids_csv (comma-separated document IDs), top_k (int, default 5)."
    ),
)
