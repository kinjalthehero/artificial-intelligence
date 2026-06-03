import asyncio

from llama_index.core.tools import FunctionTool

from app.services.vector_store import vector_store


def search_knowledge_base(query: str, document_ids_csv: str, top_k: int = 5) -> str:
    doc_ids = [d.strip() for d in document_ids_csv.split(",") if d.strip()]
    if not doc_ids:
        return "No document IDs provided."

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


search_tool = FunctionTool.from_defaults(
    fn=search_knowledge_base,
    name="search_knowledge_base",
    description=(
        "Search the vector knowledge base for document chunks relevant to a query. "
        "Parameters: query (str), document_ids_csv (comma-separated document IDs), top_k (int, default 5)."
    ),
)
