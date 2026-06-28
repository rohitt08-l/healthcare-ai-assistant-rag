from typing import Dict, Any, List, Optional

from src.rag.rag import rag


# -------------------------------------------------------------------
# Static appointment data
# -------------------------------------------------------------------

appointments = [
    {
        "slot_id": "APT-001",
        "doctor": "Dr. Sharma",
        "specialization": "General Physician",
        "date": "2026-07-01",
        "time": "10:00 AM",
        "available": True,
        "location": "Clinic Room 101",
        "consultation_type": "In-person",
    },
    {
        "slot_id": "APT-002",
        "doctor": "Dr. Mehta",
        "specialization": "Cardiologist",
        "date": "2026-07-01",
        "time": "12:00 PM",
        "available": True,
        "location": "Clinic Room 205",
        "consultation_type": "In-person",
    },
    {
        "slot_id": "APT-003",
        "doctor": "Dr. Patil",
        "specialization": "Dermatologist",
        "date": "2026-07-02",
        "time": "04:00 PM",
        "available": True,
        "location": "Clinic Room 110",
        "consultation_type": "Video Consultation",
    },
    {
        "slot_id": "APT-004",
        "doctor": "Dr. Rao",
        "specialization": "General Physician",
        "date": "2026-07-03",
        "time": "11:30 AM",
        "available": True,
        "location": "Clinic Room 102",
        "consultation_type": "In-person",
    },
    {
        "slot_id": "APT-005",
        "doctor": "Dr. Iyer",
        "specialization": "Pulmonologist",
        "date": "2026-07-03",
        "time": "03:00 PM",
        "available": True,
        "location": "Clinic Room 301",
        "consultation_type": "In-person",
    },
    {
        "slot_id": "APT-006",
        "doctor": "Dr. Kulkarni",
        "specialization": "Orthopedic",
        "date": "2026-07-04",
        "time": "09:30 AM",
        "available": True,
        "location": "Clinic Room 210",
        "consultation_type": "In-person",
    },
    {
        "slot_id": "APT-007",
        "doctor": "Dr. Nair",
        "specialization": "Neurologist",
        "date": "2026-07-04",
        "time": "01:00 PM",
        "available": True,
        "location": "Clinic Room 305",
        "consultation_type": "Video Consultation",
    },
    {
        "slot_id": "APT-008",
        "doctor": "Dr. Deshmukh",
        "specialization": "Endocrinologist",
        "date": "2026-07-05",
        "time": "10:45 AM",
        "available": True,
        "location": "Clinic Room 220",
        "consultation_type": "In-person",
    },
]


# -------------------------------------------------------------------
# RAG tool
# -------------------------------------------------------------------

def rag_tool(query: str, user_id: str) -> Dict[str, Any]:
    """
    Retrieve relevant document chunks from ChromaDB.
    """

    return rag.retrieve(
        query=query,
        user_id=user_id,
        top_k=5,
    )


# -------------------------------------------------------------------
# Appointment helper functions
# -------------------------------------------------------------------

def infer_specialization_from_reason(reason: str) -> Optional[str]:
    """
    Simple keyword-based specialization inference.

    Examples:
    - chest pain -> Cardiologist
    - skin allergy -> Dermatologist
    - cough or breathing issue -> Pulmonologist
    - diabetes -> Endocrinologist
    """

    if not reason:
        return None

    reason_lower = reason.lower()

    specialty_keywords = {
        "Cardiologist": [
            "heart",
            "chest pain",
            "blood pressure",
            "bp",
            "cardiac",
            "palpitation",
            "palpitations",
        ],
        "Dermatologist": [
            "skin",
            "rash",
            "allergy",
            "itching",
            "acne",
            "derma",
        ],
        "Pulmonologist": [
            "cough",
            "breathing",
            "asthma",
            "lung",
            "respiratory",
            "chest congestion",
        ],
        "Orthopedic": [
            "bone",
            "joint",
            "knee",
            "back pain",
            "fracture",
            "shoulder",
        ],
        "Neurologist": [
            "headache",
            "migraine",
            "nerve",
            "seizure",
            "dizziness",
        ],
        "Endocrinologist": [
            "diabetes",
            "thyroid",
            "hormone",
            "sugar",
            "insulin",
        ],
        "General Physician": [
            "fever",
            "cold",
            "body pain",
            "weakness",
            "general",
            "checkup",
        ],
    }

    for specialization, keywords in specialty_keywords.items():
        for keyword in keywords:
            if keyword in reason_lower:
                return specialization

    return "General Physician"


def get_available_slots() -> List[Dict[str, Any]]:
    """
    Return all available appointment slots.
    """

    return [
        slot
        for slot in appointments
        if slot["available"]
    ]


def filter_slots(
    preferred_date: str = "",
    specialization: str = "",
) -> List[Dict[str, Any]]:
    """
    Filter available slots by preferred date and/or specialization.
    """

    slots = get_available_slots()

    if preferred_date:
        slots = [
            slot
            for slot in slots
            if slot["date"] == preferred_date
        ]

    if specialization:
        slots = [
            slot
            for slot in slots
            if slot["specialization"].lower() == specialization.lower()
        ]

    return slots


def get_nearest_slots(
    specialization: str = "",
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Return nearest available appointment slots.
    """

    slots = get_available_slots()

    if specialization:
        specialty_slots = [
            slot
            for slot in slots
            if slot["specialization"].lower() == specialization.lower()
        ]

        if specialty_slots:
            slots = specialty_slots

    slots = sorted(
        slots,
        key=lambda item: (item["date"], item["time"]),
    )

    return slots[:limit]


def book_slot_by_id(
    slot_id: str,
    reason: str = "",
) -> Dict[str, Any]:
    """
    Book appointment using slot_id.
    """

    for slot in appointments:
        if slot["slot_id"].lower() == slot_id.lower():
            if not slot["available"]:
                return {
                    "status": "already_booked",
                    "message": f"Slot {slot_id} is already booked.",
                    "slot": slot,
                }

            slot["available"] = False

            return {
                "status": "booked",
                "message": "Appointment booked successfully.",
                "appointment": slot,
                "reason": reason,
            }

    return {
        "status": "slot_not_found",
        "message": f"No appointment slot found with slot_id {slot_id}.",
        "available_slots": get_available_slots(),
    }


# -------------------------------------------------------------------
# Appointment scheduler tool
# -------------------------------------------------------------------

def appointment_scheduler_tool(
    action: str = "check",
    preferred_date: str = "",
    reason: str = "",
    specialization: str = "",
    slot_id: str = "",
) -> Dict[str, Any]:
    """
    Improved appointment scheduler.

    Supported actions:
    - check: show all available appointments
    - suggest: suggest appointments based on reason, specialization, and date
    - book: book appointment using slot_id or preferred date/specialization
    """

    action = action.lower().strip() if action else "check"
    preferred_date = preferred_date.strip() if preferred_date else ""
    reason = reason.strip() if reason else ""
    specialization = specialization.strip() if specialization else ""
    slot_id = slot_id.strip() if slot_id else ""

    available_slots = get_available_slots()

    if action == "check":
        return {
            "status": "available_slots_found",
            "message": "Available appointment slots found.",
            "available_slots": available_slots,
        }

    if action == "suggest":
        inferred_specialization = specialization or infer_specialization_from_reason(reason)

        matching_slots = filter_slots(
            preferred_date=preferred_date,
            specialization=inferred_specialization or "",
        )

        if matching_slots:
            return {
                "status": "suggestions_found",
                "message": "Matching appointment suggestions found.",
                "reason": reason,
                "inferred_specialization": inferred_specialization,
                "preferred_date": preferred_date,
                "suggested_slots": matching_slots,
            }

        nearest_slots = get_nearest_slots(
            specialization=inferred_specialization or "",
            limit=3,
        )

        return {
            "status": "no_exact_match",
            "message": "No exact appointment match found, but here are the nearest available suggestions.",
            "reason": reason,
            "inferred_specialization": inferred_specialization,
            "preferred_date": preferred_date,
            "suggested_slots": nearest_slots,
        }

    if action == "book":
        inferred_specialization = specialization or infer_specialization_from_reason(reason)

        if slot_id:
            return book_slot_by_id(
                slot_id=slot_id,
                reason=reason,
            )

        matching_slots = filter_slots(
            preferred_date=preferred_date,
            specialization=inferred_specialization or "",
        )

        if matching_slots:
            selected_slot = matching_slots[0]
            selected_slot["available"] = False

            return {
                "status": "booked",
                "message": "Appointment booked successfully.",
                "appointment": selected_slot,
                "reason": reason,
                "inferred_specialization": inferred_specialization,
            }

        nearest_slots = get_nearest_slots(
            specialization=inferred_specialization or "",
            limit=3,
        )

        return {
            "status": "booking_needs_confirmation",
            "message": "No exact slot was available. Please choose one of the suggested slots.",
            "reason": reason,
            "inferred_specialization": inferred_specialization,
            "preferred_date": preferred_date,
            "suggested_slots": nearest_slots,
        }

    return {
        "status": "invalid_action",
        "message": f"Unknown appointment action: {action}",
        "available_slots": available_slots,
    }