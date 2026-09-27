"""
Doctor's free-text care plan → structured CarePlanItems. Owner: Shreyan.

Rule (from the OnKo spec): the AI may only STRUCTURE what the doctor wrote.
It must never invent a medicine, dose, test or date. The doctor reviews and
approves every item in the UI before anything is saved.
"""

from __future__ import annotations

from core import config
from core.ai.llm import chat_json
from core.contracts import TIME_SLOTS, CarePlanItem, ItemKind

SYSTEM_PROMPT = f"""You convert a doctor's care-plan text into structured items.
Return JSON: {{"items": [ {{
  "kind": one of {[k.value for k in ItemKind]},
  "name": string,             // medicine / test / appointment / treatment / instruction name
  "dose": string,             // "" if none
  "timings": [string],        // subset of {TIME_SLOTS}; [] for "as needed" or one-off events
  "start_date": "YYYY-MM-DD", // event date for tests/appointments/treatments
  "end_date": "YYYY-MM-DD" or "",
  "notes": string             // e.g. "after food", "if nausea"
}} ]}}
Rules:
- Only include what the doctor explicitly wrote. Never add medicines, doses, tests or dates.
- "twice daily" = ["morning","evening"]; "thrice daily" = ["morning","afternoon","evening"];
  "once daily"/"daily" = ["morning"] unless a time is given; "at night"/"bedtime" = ["night"].
- Convert relative dates ("days 1-14", "in 5 days", "on 3 Oct") into absolute dates using TODAY.
  "Days 1-14" of a cycle starting today means start_date=TODAY, end_date=TODAY+13 days.
- If a date is missing or unclear, use "" rather than guessing.
"""

_SAMPLE = [
    CarePlanItem(ItemKind.MEDICATION, "Capecitabine", "1500 mg", ["morning", "evening"], "", "", "after food"),
    CarePlanItem(ItemKind.TEST, "CBC", "", [], "", "", "stub data"),
]


def extract_care_plan(text: str, today: str) -> list[CarePlanItem]:
    if config.USE_STUBS:
        return [CarePlanItem(**{**i.__dict__, "start_date": today}) for i in _SAMPLE]
    data = chat_json(SYSTEM_PROMPT, f"TODAY: {today}\n\nDOCTOR'S PLAN:\n{text}")
    items: list[CarePlanItem] = []
    for raw in data.get("items", []):
        try:
            kind = ItemKind(str(raw.get("kind", "")).lower())
        except ValueError:
            kind = ItemKind.INSTRUCTION
        items.append(CarePlanItem(
            kind=kind,
            name=str(raw.get("name", "")).strip(),
            dose=str(raw.get("dose", "") or "").strip(),
            timings=[t for t in (raw.get("timings") or []) if t in TIME_SLOTS],
            start_date=str(raw.get("start_date", "") or ""),
            end_date=str(raw.get("end_date", "") or ""),
            notes=str(raw.get("notes", "") or "").strip(),
        ))
    return [i for i in items if i.name]
