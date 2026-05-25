"""RAG pipeline: chunking, embedding via Ollama, storage/retrieval via ChromaDB."""

import uuid
from pathlib import Path

import chromadb
from ollama import AsyncClient

from app.config import settings


class RAGService:
    def __init__(self) -> None:
        chroma_path = Path(settings.CHROMA_PATH)
        chroma_path.mkdir(parents=True, exist_ok=True)
        self._chroma = chromadb.PersistentClient(path=str(chroma_path))
        self._ollama = AsyncClient(host=settings.OLLAMA_HOST)

    async def _embed(self, texts: list[str]) -> list[list[float]]:
        response = await self._ollama.embed(
            model=settings.EMBEDDING_MODEL,
            input=texts,
        )
        return response.embeddings

    def _chunk_text(self, text: str, page: int, document_id: str, filename: str) -> list[dict]:
        chunk_size = settings.CHUNK_SIZE
        overlap = settings.CHUNK_OVERLAP
        chunks = []
        start = 0
        idx = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]
            if chunk_text.strip():
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "text": chunk_text,
                    "metadata": {
                        "document_id": document_id,
                        "filename": filename,
                        "chunk_index": idx,
                        "page": page,
                    },
                })
                idx += 1
            start = end - overlap

        return chunks

    async def ingest_document(
        self, document_id: str, filename: str, pages: list[dict]
    ) -> int:
        collection_name = f"doc_{document_id.replace('-', '_')}"
        collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        all_chunks = []
        for page_data in pages:
            chunks = self._chunk_text(
                page_data["text"], page_data["page"], document_id, filename
            )
            all_chunks.extend(chunks)

        if not all_chunks:
            return 0

        batch_size = 32
        for i in range(0, len(all_chunks), batch_size):
            batch = all_chunks[i : i + batch_size]
            texts = [c["text"] for c in batch]
            embeddings = await self._embed(texts)
            collection.add(
                ids=[c["id"] for c in batch],
                documents=texts,
                embeddings=embeddings,
                metadatas=[c["metadata"] for c in batch],
            )

        return len(all_chunks)

    async def query(
        self, question: str, document_ids: list[str], top_k: int | None = None
    ) -> list[dict]:
        top_k = top_k or settings.RAG_TOP_K
        query_embedding = (await self._embed([question]))[0]

        all_results = []
        for doc_id in document_ids:
            collection_name = f"doc_{doc_id.replace('-', '_')}"
            try:
                collection = self._chroma.get_collection(name=collection_name)
            except Exception:
                continue

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, collection.count()),
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
        collection_name = f"doc_{document_id.replace('-', '_')}"
        try:
            self._chroma.delete_collection(name=collection_name)
        except Exception:
            pass

    def build_rag_prompt(self, question: str, chunks: list[dict]) -> str:
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            source = chunk["filename"]
            page = chunk.get("page", "?")
            context_parts.append(
                f"[Source {i}: {source}, page {page}]\n{chunk['content']}"
            )

        context_block = "\n\n".join(context_parts)

        return (
            "Answer the question based on the following context from uploaded documents. "
            "If the context doesn't contain enough information, say so. "
            "Cite sources using [Source N] when referencing specific information.\n\n"
            f"--- CONTEXT ---\n{context_block}\n--- END CONTEXT ---\n\n"
            f"Question: {question}"
        )


rag_service = RAGService()
