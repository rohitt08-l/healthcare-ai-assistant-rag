import asyncio
import copy
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from fastapi import UploadFile

from main import health
from src.agent.agent import SimpleHealthcareAgent
from src.agent import tools as tools_module
from src.rag.rag import SimpleRAG
from src.routes.chat import ChatRequest, chat_query
from src.routes import ingest as ingest_module
from src.utils.doc_loader import load_document


class MainFeatureTests(unittest.TestCase):
    def test_health_endpoint_returns_expected_summary(self):
        response = health()

        self.assertEqual(response["message"], "Healthcare Agentic RAG API is running")
        self.assertEqual(response["endpoints"]["ingest"], "/ingest/file")
        self.assertEqual(response["endpoints"]["chat"], "/chat/query")

    def test_chat_query_forwards_request_to_agent(self):
        expected = {
            "query": "What reports do I have?",
            "user_id": "user-123",
            "selected_tool": "rag_tool",
            "answer": "Here are the reports",
        }

        with patch("src.routes.chat.healthcare_agent.run", return_value=expected) as run_mock:
            response = chat_query(ChatRequest(user_id="user-123", query="What reports do I have?"))

        self.assertEqual(response, expected)
        run_mock.assert_called_once_with(query="What reports do I have?", user_id="user-123")

    def test_ingest_file_saves_upload_and_ingests_documents(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "sample.txt")
            with open(temp_file, "w", encoding="utf-8") as handle:
                handle.write("sample document content")

            handle = open(temp_file, "rb")
            upload_file = UploadFile(filename="sample.txt", file=handle)

            try:
                with patch.object(ingest_module, "UPLOAD_DIR", temp_dir), \
                     patch("src.routes.ingest.load_document", return_value=[{"text": "sample document content", "metadata": {"source": "sample.txt"}}]) as load_mock, \
                     patch("src.routes.ingest.rag.ingest_documents", return_value={"total_chunks": 1}) as ingest_mock:
                    response = asyncio.run(ingest_module.ingest_file(user_id="user-42", file=upload_file))
            finally:
                handle.close()

            self.assertEqual(response["filename"], "sample.txt")
            self.assertEqual(response["user_id"], "user-42")
            self.assertEqual(response["result"], {"total_chunks": 1})
            load_mock.assert_called_once()
            ingest_mock.assert_called_once()
            self.assertTrue(os.path.exists(os.path.join(temp_dir, "sample.txt")))

    def test_load_document_supports_text_files_and_rejects_unknown_types(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            txt_path = os.path.join(temp_dir, "notes.txt")
            with open(txt_path, "w", encoding="utf-8") as handle:
                handle.write("hello world")

            documents = load_document(txt_path)

            self.assertEqual(len(documents), 1)
            self.assertEqual(documents[0]["text"], "hello world")
            self.assertEqual(documents[0]["metadata"]["file_type"], "txt")

            unsupported_path = os.path.join(temp_dir, "notes.bin")
            with open(unsupported_path, "wb") as handle:
                handle.write(b"data")

            with self.assertRaises(ValueError):
                load_document(unsupported_path)

    def test_agent_tool_helpers_and_scheduler_flow(self):
        self.assertEqual(tools_module.infer_specialization_from_reason("chest pain"), "Cardiologist")
        self.assertEqual(tools_module.infer_specialization_from_reason("skin rash"), "Dermatologist")
        self.assertEqual(tools_module.infer_specialization_from_reason("unknown complaint"), "General Physician")

        with patch.object(tools_module, "appointments", copy.deepcopy(tools_module.appointments)):
            slots = tools_module.filter_slots(preferred_date="2026-07-01", specialization="General Physician")
            self.assertEqual([slot["slot_id"] for slot in slots], ["APT-001"])

            check_result = tools_module.appointment_scheduler_tool(action="check")
            self.assertEqual(check_result["status"], "available_slots_found")
            self.assertGreaterEqual(len(check_result["available_slots"]), 1)

            suggestion_result = tools_module.appointment_scheduler_tool(
                action="suggest",
                reason="I have chest pain",
                preferred_date="2026-07-01",
            )
            self.assertEqual(suggestion_result["status"], "suggestions_found")
            self.assertEqual(suggestion_result["suggested_slots"][0]["slot_id"], "APT-002")

    def test_booking_helper_returns_expected_statuses(self):
        with patch.object(tools_module, "appointments", copy.deepcopy(tools_module.appointments)):
            booked = tools_module.book_slot_by_id("APT-002", reason="heart issue")
            self.assertEqual(booked["status"], "booked")
            self.assertFalse(booked["appointment"]["available"])

            duplicate = tools_module.book_slot_by_id("APT-002", reason="again")
            self.assertEqual(duplicate["status"], "already_booked")

            missing = tools_module.book_slot_by_id("APT-999")
            self.assertEqual(missing["status"], "slot_not_found")

    def test_rag_chunking_and_retrieval_helpers(self):
        rag_instance = SimpleRAG.__new__(SimpleRAG)
        rag_instance.collection = MagicMock()

        chunks = rag_instance.chunk_text("hello world", chunk_size=5, chunk_overlap=2)
        self.assertEqual(chunks[0], "hello")
        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(rag_instance.chunk_text("", chunk_size=5, chunk_overlap=2), [])

        with patch("src.rag.rag.bge_embeddings.embed_query", return_value=[0.1, 0.2]):
            result = rag_instance.ingest_documents(
                documents=[{"text": "sample text", "metadata": {"source": "doc.txt"}}],
                user_id="user-1",
            )

        self.assertGreaterEqual(result["total_chunks"], 1)
        rag_instance.collection.add.assert_called_once()

        rag_instance.collection.query.return_value = {
            "documents": [["sample text"]],
            "metadatas": [[{"user_id": "user-1"}]],
            "distances": [[0.12]],
        }

        with patch("src.rag.rag.bge_embeddings.embed_query", return_value=[0.3]):
            retrieval = rag_instance.retrieve("sample", "user-1", top_k=1)

        self.assertEqual(retrieval["query"], "sample")
        self.assertEqual(len(retrieval["results"]), 1)
        self.assertEqual(retrieval["results"][0]["metadata"]["user_id"], "user-1")

    def test_agent_json_parsing_fallback(self):
        agent = SimpleHealthcareAgent.__new__(SimpleHealthcareAgent)

        parsed = agent.extract_json('{"tool": "rag_tool", "args": {"reason": "test"}}')
        self.assertEqual(parsed["tool"], "rag_tool")

        embedded = agent.extract_json("prefix {\"tool\": \"appointment_scheduler_tool\", \"args\": {\"action\": \"check\"}} suffix")
        self.assertEqual(embedded["tool"], "appointment_scheduler_tool")

        fallback = agent.extract_json("not json at all")
        self.assertEqual(fallback["tool"], "rag_tool")


if __name__ == "__main__":
    unittest.main()
