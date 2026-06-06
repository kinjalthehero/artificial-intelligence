"""
Text Chunking Service (LlamaIndex SentenceSplitter)
====================================================
Splits extracted document text into overlapping chunks for embedding and retrieval.

Why chunking?
- LLMs have context limits — you can't feed an entire 100-page PDF into a prompt
- Smaller chunks allow more precise retrieval (find the exact relevant paragraph)
- Overlapping chunks prevent information loss at chunk boundaries

Why LlamaIndex SentenceSplitter (vs. naive character splitting)?
- Respects sentence boundaries: won't split mid-sentence
- Semantic coherence: each chunk is a complete thought
- Configurable overlap: connects adjacent chunks for context continuity
- Industry standard in RAG pipelines

Chunk size of 512 tokens with 50-token overlap is a good balance between
precision (smaller chunks = more precise retrieval) and context (larger chunks
= more surrounding context for the LLM to work with).
"""

import uuid

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document as LIDocument

from app.core.config import settings


class ChunkingService:
    def __init__(self) -> None:
        # SentenceSplitter splits text at sentence boundaries, not arbitrary character positions
        self._splitter = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,  # Max tokens per chunk (512)
            chunk_overlap=settings.CHUNK_OVERLAP,  # Overlap between chunks (50 tokens)
        )

    def chunk_document(
        self, pages: list[dict], document_id: str, filename: str
    ) -> list[dict]:
        """Convert parsed document pages into chunks with metadata.

        Flow: pages → LlamaIndex Document objects → SentenceSplitter → nodes → chunk dicts
        Each chunk gets a unique UUID, the original text, and metadata (document ID,
        filename, chunk index, page number) for citation tracking.
        """
        all_nodes = []
        for page_data in pages:
            # Wrap each page as a LlamaIndex Document with metadata
            doc = LIDocument(
                text=page_data["text"],
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_data["page"],
                },
            )
            # Split into nodes (chunks) respecting sentence boundaries
            nodes = self._splitter.get_nodes_from_documents([doc])
            all_nodes.extend(nodes)

        # Convert LlamaIndex nodes to simple dicts for ChromaDB storage
        return [
            {
                "id": str(uuid.uuid4()),
                "text": node.get_content(),
                "metadata": {
                    "document_id": document_id,
                    "filename": filename,
                    "chunk_index": i,
                    "page": node.metadata.get("page", 1),
                },
            }
            for i, node in enumerate(all_nodes)
        ]


chunking_service = ChunkingService()
