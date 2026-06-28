import logging
from typing import List

import requests
from langchain_core.embeddings import Embeddings

from src.config.settings import settings

logger = logging.getLogger(__name__)


class OllamaBGEEmbeddings(Embeddings):
    """
    Simple LangChain-compatible embeddings wrapper using Ollama bge-m3.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_EMBEDDING_MODEL
        self.embedding_dimension = 1024

        logger.info(
            "Initialized Ollama embeddings with model=%s, base_url=%s",
            self.model,
            self.base_url,
        )

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        return text.replace("\n", " ").strip()

    def _zero_vector(self) -> List[float]:
        return [0.0] * self.embedding_dimension

    def _embed(self, text: str) -> List[float]:
        text = self._clean_text(text)

        if not text:
            return self._zero_vector()

        url = f"{self.base_url}/api/embeddings"

        payload = {
            "model": self.model,
            "prompt": text,
        }

        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        data = response.json()
        embedding = data.get("embedding")

        if embedding is None:
            raise ValueError(f"No embedding returned from Ollama: {data}")

        return embedding

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        logger.info("Embedding %s documents using %s", len(texts), self.model)
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)


bge_embeddings = OllamaBGEEmbeddings()