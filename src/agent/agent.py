import json
import logging
import re
from typing import Dict, Any

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

from src.config.settings import settings
from src.agent.tools import rag_tool, appointment_scheduler_tool

logger = logging.getLogger(__name__)


ROUTER_SYSTEM_PROMPT = """
You are a simple healthcare assistant router.

Your task is to decide which tool should be used for the user query.

Available tools:

1. rag_tool
Use this when the user asks about:
- reports
- healthcare records
- symptoms from uploaded documents
- diseases from uploaded documents
- medication information from uploaded documents
- medical document search
- patient history
- current user reports

2. appointment_scheduler_tool
Use this when the user asks to:
- check appointments
- list appointments
- view available appointment slots
- suggest a doctor appointment
- schedule an appointment
- book a doctor appointment
- find appointment slots

Return ONLY valid JSON.

JSON format:
{
  "tool": "rag_tool" or "appointment_scheduler_tool",
  "args": {
    "action": "check" or "suggest" or "book",
    "preferred_date": "YYYY-MM-DD if mentioned else empty",
    "reason": "short reason from user query",
    "specialization": "doctor specialization if clearly mentioned else empty",
    "slot_id": "appointment slot id if mentioned else empty"
  }
}

Rules:
- If user asks only to see/list/check appointments, use action="check".
- If user describes a health issue and asks for an appointment suggestion, use action="suggest".
- If user asks to book/schedule an appointment, use action="book".
- If the user mentions a slot id like APT-002, include it in slot_id.
- If the user mentions a date, convert it to YYYY-MM-DD.
- If no date is mentioned, keep preferred_date empty.
- If no specialization is clearly mentioned, keep specialization empty.
"""


FINAL_ANSWER_SYSTEM_PROMPT = """
You are a helpful healthcare assistant.

Important rules:
- Use only the provided tool result/context.
- Do not invent doctors, appointments, medications, diagnoses, or document facts.
- For document questions, answer only from retrieved context.
- For appointment results, clearly show doctor name, specialization, date, time, slot id, location, and consultation type.
- If appointment suggestions are returned, ask the user to choose a slot_id to book.
- If an appointment is booked, clearly confirm the booking.
- Do not claim to be a doctor.
- If medical guidance is needed, recommend consulting a qualified doctor.
- Be concise and clear.
"""


class SimpleHealthcareAgent:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_REASONING_MODEL

        logger.info(
            "Initializing ChatOllama with model=%s, base_url=%s",
            self.model,
            self.base_url,
        )

        self.llm = ChatOllama(
            model=self.model,
            base_url=self.base_url,
            reasoning=False,
        )

    def extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response.
        """

        logger.info("Extracting JSON from router response")

        try:
            return json.loads(text)
        except Exception:
            pass

        match = re.search(r"\{.*\}", text, re.DOTALL)

        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass

        logger.warning("Could not parse router response as JSON. Falling back to rag_tool.")

        return {
            "tool": "rag_tool",
            "args": {
                "preferred_date": "",
                "reason": "",
            },
        }

    def decide_tool(self, query: str) -> Dict[str, Any]:
        """
        Ask LLM to decide which tool to use.
        """

        logger.info("Deciding tool for query: %s", query)

        messages = [
            SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            HumanMessage(content=query),
        ]

        response = self.llm.invoke(messages)

        raw_response = response.content.strip()

        logger.info("Router raw response: %s", raw_response)

        decision = self.extract_json(raw_response)

        logger.info("Parsed router decision: %s", decision)

        return decision

    def generate_final_answer(
        self,
        query: str,
        tool_name: str,
        tool_result: Dict[str, Any],
    ) -> str:
        """
        Generate final user-facing response using tool result.
        """

        logger.info("Generating final answer using tool: %s", tool_name)

        user_prompt = f"""
            User query:
            {query}

            Tool used:
            {tool_name}

            Tool result:
            {json.dumps(tool_result, indent=2)}

        Now provide the final answer to the user.
        """

        messages = [
            SystemMessage(content=FINAL_ANSWER_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)

        final_answer = response.content.strip()

        logger.info("Final answer generated successfully")

        return final_answer

    def run(self, query: str, user_id: str) -> Dict[str, Any]:
        """
        Main agent execution flow.
        """

        logger.info("Agent run started")
        logger.info("User ID: %s", user_id)
        logger.info("Query: %s", query)

        decision = self.decide_tool(query)

        tool_name = decision.get("tool", "rag_tool")
        args = decision.get("args", {})

        logger.info("Selected tool: %s", tool_name)
        logger.info("Tool args: %s", args)

        if tool_name == "appointment_scheduler_tool":
            action = args.get("action", "check")
            preferred_date = args.get("preferred_date", "")
            reason = args.get("reason", query)
            specialization = args.get("specialization", "")
            slot_id = args.get("slot_id", "")

            tool_result = appointment_scheduler_tool(
                action=action,
                preferred_date=preferred_date,
                reason=reason,
                specialization=specialization,
                slot_id=slot_id,
            )

        else:
            tool_name = "rag_tool"

            logger.info("Calling rag_tool for user_id=%s", user_id)

            tool_result = rag_tool(
                query=query,
                user_id=user_id,
            )

        logger.info("Tool execution completed")

        final_answer = self.generate_final_answer(
            query=query,
            tool_name=tool_name,
            tool_result=tool_result,
        )

        logger.info("Agent run completed successfully")

        return {
            "query": query,
            "user_id": user_id,
            "selected_tool": tool_name,
            "tool_result": tool_result,
            "answer": final_answer,
        }


healthcare_agent = SimpleHealthcareAgent()
