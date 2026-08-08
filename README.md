# Healthcare AI Assistant RAG

A learning-focused **Agentic Healthcare RAG Assistant** built with **FastAPI**, **Ollama**, **ChromaDB**, and **Streamlit**.

This project demonstrates how to build a simple agentic workflow where a user can:

- Upload healthcare documents such as PDF, DOCX, or TXT files
- Generate embeddings using the local Ollama `bge-m3` embedding model
- Store document chunks in ChromaDB
- Ask questions over uploaded documents using RAG
- Route appointment-related queries to a simple appointment scheduler tool
- Use a local reasoning LLM through Ollama, such as `gpt-oss:20b`
- Interact through API endpoints or a Streamlit UI

> This project is created for learning purposes only. It should not be used for real medical diagnosis, treatment, or clinical decision-making.

---

## Overview

The application uses an agentic architecture with two main tools:

1. **RAG Tool**
   - Retrieves relevant document chunks from ChromaDB
   - Generates embeddings with Ollama `bge-m3`
   - Uses a vector search flow for document retrieval

2. **Appointment Scheduler Tool**
   - Uses static appointment data
   - Handles simple booking and availability queries

A reasoning LLM decides which tool to use, and the selected tool output is combined into the final response.

---

## Features

- FastAPI backend with `/health`, `/ingest`, and `/ask`
- Streamlit user interface for upload and chat
- File ingestion for PDF, DOCX, and TXT
- Ollama-based embeddings and reasoning
- ChromaDB vector store
- Simple tool routing for document search vs. appointments
- Local-first and Docker-friendly setup
- Environment-based configuration

---

## Requirements

- Python 3.11
- `pip`
- Ollama server accessible at the configured base URL
- Docker (optional)

---

## Setup

1. Clone the repository:

```bash
git clone https://github.com/<your-repo>/healthcare-ai-assistant-rag.git
cd healthcare-ai-assistant-rag
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
.\.venv\Scriptsctivate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create or update `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_EMBEDDING_MODEL=bge-m3
OLLAMA_REASONING_MODEL=gpt-oss:20b
CHROMA_PATH=./chroma_db
CHROMA_COLLECTION=healthcare_docs
```

5. Start Ollama and ensure the required models are available:

- `bge-m3` for embedding generation
- `gpt-oss:20b` for reasoning/chat

---

## Running Locally

Start the FastAPI application:

```bash
python main.py
```

Launch the Streamlit UI:

```bash
streamlit run streamlit/streamlit_app.py
```

Open:

- Streamlit app: `http://localhost:8501`
- FastAPI Swagger docs: `http://localhost:8000/docs`

--

## Docker

Build and run the app with Docker Compose:

```bash
docker-compose up --build
```

The service is exposed on port `8000`.

> If you use Docker on Windows and run Ollama on the host, `host.docker.internal` is configured in `docker-compose.yml` for container-to-host network access.

---

## Configuration

The application reads settings from `.env` and environment variables via `python-dotenv`.

- `OLLAMA_BASE_URL`: Ollama server URL
- `OLLAMA_EMBEDDING_MODEL`: Embedding model name
- `OLLAMA_REASONING_MODEL`: Reasoning/chat model name
- `CHROMA_PATH`: ChromaDB storage location
- `CHROMA_COLLECTION`: ChromaDB collection name

--

## API Endpoints

### Health

```http
GET /health
```

Returns a simple status payload.

### Ingest File

```http
POST /ingest
```

Form data:

- `user_id` (string)
- `file` (uploaded PDF, DOCX, or TXT)

Example:

```bash
curl -X POST "http://localhost:8000/ingest"   -F "user_id=user123"   -F "file=@report.pdf"
```

### Ask Query

```http
POST /ask
```

JSON body:

```json
{
  "user_id": "user123",
  "query": "What does my report say about blood pressure?"
}
```

--

## Streamlit UI

The Streamlit app includes:

- Settings for server URL and user ID
- Document upload and ingestion
- Chat interface for queries
- Display of retrieval excerpts and appointment responses
- Connection and error reporting

--

## Project Structure

```text
healthcare-ai-assistant-rag/
│
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env
├── README.md
│
├── src/
│   ├── config/
│   │   └── settings.py
│   ├── routes/
│   │   ├── ingest.py
│   │   └── chat.py
│   ├── rag/
│   │   ├── embeddings.py
│   │   └── rag.py
│   ├── agent/
│   │   ├── agent.py
│   │   └── tools.py
│   ├── utils/
│   │   └── doc_loader.py
│   └── streamlit/
│       └── streamlit_app.py
├── uploaded_files/
├── chroma_db/
└── data/
```

--

## Notes

- Ollama must be running before ingesting documents or querying the RAG agent.
- If embedding requests fail, verify `OLLAMA_BASE_URL` and model availability.
- The appointment scheduler is a mock tool and not suitable for production.

--

## Troubleshooting

- `ConnectionTimeout` when calling Ollama: confirm the host and port are reachable.
- `ImportError: cannot import name 'load_document'`: ensure `src/utils/doc_loader.py` exists and exports `load_document`.
- Run `pip install -r requirements.txt` if dependencies are missing.

--

