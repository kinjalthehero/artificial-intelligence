import uuid

from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import Document as LIDocument

from app.core.config import settings


class ChunkingService:
    def __init__(self) -> None:
        self._splitter = SentenceSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def chunk_document(
        self, pages: list[dict], document_id: str, filename: str
    ) -> list[dict]:
        all_nodes = []
        for page_data in pages:
            doc = LIDocument(
                text=page_data["text"],
                metadata={
                    "document_id": document_id,
                    "filename": filename,
                    "page": page_data["page"],
                },
            )
            nodes = self._splitter.get_nodes_from_documents([doc])
            all_nodes.extend(nodes)

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
