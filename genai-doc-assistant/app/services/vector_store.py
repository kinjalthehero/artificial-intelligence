"""
Vector Store Service (ChromaDB)
================================
Stores and retrieves document chunk embeddings using ChromaDB.

What is a vector store?
- A database optimized for storing and searching high-dimensional vectors (embeddings)
- Enables "similarity search": given a query vector, find the most similar stored vectors
- This is the core of RAG — finding relevant document chunks for a question

Why ChromaDB?
- Embedded mode: runs in-process, no separate server to manage (like SQLite for vectors)
- Persistent: data survives server restarts (stored on disk)
- Cosine similarity: measures angle between vectors (standard for text similarity)
- Free and open source
- Simple API: add, query, delete

Architecture: each uploaded document gets its own ChromaDB collection (doc_{uuid}).
This isolates documents so deleting one doesn't affect others, and queries can
target specific documents via their IDs.
"""

from pathlib import Path

import chromadb

from app.core.config import settings
from app.core.logging_config import get_logger
from app.services.embedding_service import embedding_service

logger = get_logger(__name__)


class VectorStore:
    def __init__(self) -> None:
        chroma_path = Path(settings.CHROMA_PATH)
        chroma_path.mkdir(parents=True, exist_ok=True)
        # PersistentClient stores data on disk (survives restarts)
        # vs. EphemeralClient which is in-memory only
        self._chroma = chromadb.PersistentClient(path=str(chroma_path))

    def _collection_name(self, document_id: str) -> str:
        """Each document gets its own collection: doc_{uuid} (dashes replaced with underscores
        because ChromaDB collection names don't allow dashes)."""
        return f"doc_{document_id.replace('-', '_')}"

    async def ingest(self, document_id: str, chunks: list[dict]) -> int:
        """Store document chunks with their embeddings in ChromaDB.

        Process:
        1. Create a ChromaDB collection for this document (cosine similarity metric)
        2. Batch chunks in groups of 32 (efficient for the embedding API)
        3. For each batch: generate embeddings via Gemini, then store in ChromaDB

        Each chunk is stored with its text, embedding vector, and metadata
        (document_id, filename, chunk_index, page) for citation tracking.
        """
        if not chunks:
            return 0

        collection_name = self._collection_name(document_id)
        collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity for retrieval
        )

        # Process in batches of 32 to avoid overwhelming the embedding API
        batch_size = 32
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c["text"] for c in batch]
            embeddings = await embedding_service.embed(texts)
            collection.add(
                ids=[c["id"] for c in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[c["metadata"] for c in batch],
            )

        logger.info("ingested_chunks", document_id=document_id, count=len(chunks))
        return len(chunks)

    async def query(
        self, question: str, document_ids: list[str], top_k: int | None = None
    ) -> list[dict]:
        """Find the most relevant document chunks for a question.

        Process:
        1. Embed the question into a vector (same vector space as the stored chunks)
        2. For each document, query its ChromaDB collection for the nearest vectors
        3. Convert distance to similarity score: score = 1.0 - cosine_distance
        4. Merge results across documents, sort by score, return top-K

        The cosine distance ranges from 0 (identical) to 2 (opposite).
        We convert to similarity: 1.0 = perfect match, 0.0 = completely unrelated.
        """
        top_k = top_k or settings.RAG_TOP_K
        query_embedding = await embedding_service.embed_single(question)

        all_results = []
        for doc_id in document_ids:
            collection_name = self._collection_name(doc_id)
            try:
                collection = self._chroma.get_collection(name=collection_name)
            except Exception:
                continue  # Document may have been deleted

            count = collection.count()
            if count == 0:
                continue

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, count),
                include=["documents", "metadatas", "distances"],
            )

            if results["ids"] and results["ids"][0]:
                for j, doc_text in enumerate(results["documents"][0]):
                    meta = results["metadatas"][0][j]
                    distance = results["distances"][0][j]
                    score = 1.0 - distance  # Convert distance to similarity
                    all_results.append({
                        "document_id": meta.get("document_id", doc_id),
                        "filename": meta.get("filename", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                        "page": meta.get("page", 1),
                        "content": doc_text,
                        "score": round(score, 4),
                    })

        # Sort all results by relevance score (highest first) and return top-K
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def delete_collection(self, document_id: str) -> None:
        """Delete a document's vector collection (called when user deletes a document)."""
        collection_name = self._collection_name(document_id)
        try:
            self._chroma.delete_collection(name=collection_name)
            logger.info("deleted_collection", document_id=document_id)
        except Exception:
            pass


vector_store = VectorStore()
