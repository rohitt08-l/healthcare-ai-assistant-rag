import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    OLLAMA_BASE_URL: str = os.getenv(
        "OLLAMA_BASE_URL",
        # "http://host.docker.internal:11434"
        "http://localhost:11434"

    )

    OLLAMA_EMBEDDING_MODEL: str = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "bge-m3"
    )

    OLLAMA_REASONING_MODEL: str = os.getenv(
        "OLLAMA_REASONING_MODEL",
        "gpt-oss:20b"
    )

    CHROMA_PATH: str = os.getenv(
        "CHROMA_PATH",
        "./chroma_db"
    )

    CHROMA_COLLECTION: str = os.getenv(
        "CHROMA_COLLECTION",
        "healthcare_docs"
    )


settings = Settings()