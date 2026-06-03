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
        self._chroma = chromadb.PersistentClient(path=str(chroma_path))

    def _collection_name(self, document_id: str) -> str:
        return f"doc_{document_id.replace('-', '_')}"

    async def ingest(self, document_id: str, chunks: list[dict]) -> int:
        if not chunks:
            return 0

        collection_name = self._collection_name(document_id)
        collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

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
        top_k = top_k or settings.RAG_TOP_K
        query_embedding = await embedding_service.embed_single(question)

        all_results = []
        for doc_id in document_ids:
            collection_name = self._collection_name(doc_id)
            try:
                collection = self._chroma.get_collection(name=collection_name)
            except Exception:
                continue

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
                    score = 1.0 - distance
                    all_results.append({
                        "document_id": meta.get("document_id", doc_id),
                        "filename": meta.get("filename", ""),
                        "chunk_index": meta.get("chunk_index", 0),
                        "page": meta.get("page", 1),
                        "content": doc_text,
                        "score": round(score, 4),
                    })

        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def delete_collection(self, document_id: str) -> None:
        collection_name = self._collection_name(document_id)
        try:
            self._chroma.delete_collection(name=collection_name)
            logger.info("deleted_collection", document_id=document_id)
        except Exception:
            pass


vector_store = VectorStore()
