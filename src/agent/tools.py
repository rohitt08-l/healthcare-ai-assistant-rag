from typing import Dict, Any, List
from datetime import datetime

from src.rag.rag import rag


appointments = [
    {
        "doctor": "Dr. Sharma",
        "specialization": "General Physician",
        "date": "2026-07-01",
        "time": "10:00 AM",
        "available": True,
    },
    {
        "doctor": "Dr. Mehta",
        "specialization": "Cardiologist",
        "date": "2026-07-01",
        "time": "12:00 PM",
        "available": True,
    },
    {
        "doctor": "Dr. Patil",
        "specialization": "Dermatologist",
        "date": "2026-07-02",
        "time": "04:00 PM",
        "available": True,
    },
    {
        "doctor": "Dr. Rao",
        "specialization": "General Physician",
        "date": "2026-07-03",
        "time": "11:30 AM",
        "available": True,
    },
]


def rag_tool(query: str, user_id: str) -> Dict[str, Any]:
    """
    Tool for retrieving healthcare documents/reports from ChromaDB.
    """

    return rag.retrieve(
        query=query,
        user_id=user_id,
        top_k=5,
    )


def appointment_scheduler_tool(
    preferred_date: str,
    reason: str = "",
) -> Dict[str, Any]:
    """
    Simple appointment scheduler tool using static appointment data.

    preferred_date format should be YYYY-MM-DD.
    """

    matching_slots: List[Dict[str, Any]] = []

    for slot in appointments:
        if slot["date"] == preferred_date and slot["available"]:
            matching_slots.append(slot)

    if not matching_slots:
        return {
            "status": "not_available",
            "message": f"No available appointments found for {preferred_date}",
            "available_slots": appointments,
        }

    selected_slot = matching_slots[0]
    selected_slot["available"] = False

    return {
        "status": "booked",
        "message": "Appointment booked successfully",
        "appointment": selected_slot,
        "reason": reason,
    }


def get_available_appointments() -> List[Dict[str, Any]]:
    return appointments
