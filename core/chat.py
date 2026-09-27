"""
Patient chatbot + doctor "since last visit" summary. Owner: Samprada.

Flow for every patient message:
  1. Save the message to memory (so it becomes history too)
  2. Danger-word check → urgent reply + SOS entry (no LLM involved)
  3. Otherwise → memory.ask() (Hindsight reflect with directives)
"""

from __future__ import annotations

from datetime import datetime, timedelta

from core import db, memory
from core.contracts import ChatReply, Entry, EntryType, Role

DANGER_TERMS = [
    "can't breathe", "cannot breathe", "breathing difficulty", "chest pain",
    "unconscious", "fainted", "seizure", "vomiting blood", "blood in vomit",
    "black stool", "heavy bleeding", "severe bleeding", "suicide", "sos",
]

EMERGENCY_REPLY = (
    "🚨 This sounds urgent. Please contact your doctor or go to the nearest "
    "emergency department right now. If you can't get there, call 108 (ambulance). "
    "I've flagged this for your care team."
)

PATIENT_CONTEXT = (
    "The person asking is the patient. Answer from what is recorded in memory, "
    "cite who recorded it and when, and follow all directives."
)


def _is_danger(text: str) -> bool:
    t = text.lower()
    return any(term in t for term in DANGER_TERMS)


def handle_message(patient_id: int, text: str, role: Role = Role.PATIENT) -> ChatReply:
    memory.save_entry(Entry(patient_id, f"{role.value} said: {text}", role, EntryType.CHAT))

    if _is_danger(text):
        memory.save_entry(Entry(patient_id, f"SOS / danger words in message: {text}", role, EntryType.SOS))
        return ChatReply(EMERGENCY_REPLY, is_emergency=True, flagged_for_doctor=True)

    answer = memory.ask(patient_id, text, context=PATIENT_CONTEXT)
    memory.save_entry(Entry(patient_id, f"OnKo answered: {answer}", role, EntryType.CHAT, metadata={"speaker": "assistant"}))
    return ChatReply(answer)


def since_last_visit(patient_id: int) -> str:
    """Doctor-facing factual summary of everything recorded since the last review."""
    since = db.last_reviewed(patient_id) or (datetime.now() - timedelta(days=30))
    question = (
        f"Summarize everything recorded for this patient since {since:%d %b %Y}. "
        "Use these headings: Missed or late medicines; Symptoms reported (with dates and any "
        "repeating patterns); New reports (values only, no interpretation); Diary and visit notes; "
        "Questions or SOS events. Be factual and brief. Do not interpret or recommend."
    )
    return memory.ask(patient_id, question, context="The person asking is the treating doctor preparing for a consultation.")
