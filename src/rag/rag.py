import uuid
from typing import List, Dict, Any

import chromadb

from src.config.settings import settings
from src.rag.embeddings import bge_embeddings


class SimpleRAG:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PATH)

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )

    def chunk_text(
        self,
        text: str,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
    ) -> List[str]:
        text = text.strip()

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]

            chunks.append(chunk)

            start = end - chunk_overlap

        return chunks

    def ingest_documents(
        self,
        documents: List[Dict[str, Any]],
        user_id: str,
    ) -> Dict[str, Any]:
        all_chunks = []
        all_embeddings = []
        all_metadatas = []
        all_ids = []

        for doc in documents:
            text = doc["text"]
            base_metadata = doc["metadata"]

            chunks = self.chunk_text(text)

            for chunk_index, chunk in enumerate(chunks):
                chunk_id = str(uuid.uuid4())

                metadata = {
                    **base_metadata,
                    "user_id": user_id,
                    "chunk_index": chunk_index,
                }

                embedding = bge_embeddings.embed_query(chunk)

                all_ids.append(chunk_id)
                all_chunks.append(chunk)
                all_embeddings.append(embedding)
                all_metadatas.append(metadata)

        if all_chunks:
            self.collection.add(
                ids=all_ids,
                documents=all_chunks,
                embeddings=all_embeddings,
                metadatas=all_metadatas,
            )

        return {
            "message": "Documents ingested successfully",
            "total_chunks": len(all_chunks),
            "user_id": user_id,
        }

    def retrieve(
        self,
        query: str,
        user_id: str,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        query_embedding = bge_embeddings.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={
                "user_id": user_id,
            },
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_docs = []

        for doc, metadata, distance in zip(documents, metadatas, distances):
            retrieved_docs.append(
                {
                    "content": doc,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return {
            "query": query,
            "results": retrieved_docs,
        }


rag = SimpleRAG()