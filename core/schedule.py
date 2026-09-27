"""
Turns the approved care plan into the patient's checklist for a given day.
Owner: Samprada.
"""

from __future__ import annotations

from datetime import date

from core import db
from core.contracts import CarePlanItem, ChecklistItem, ItemKind

_SLOT_ORDER = {"morning": 0, "afternoon": 1, "evening": 2, "night": 3, "daily": 4, "": 5}


def _active_on(item: CarePlanItem, day: str) -> bool:
    start = item.start_date or day
    end = item.end_date or (start if item.kind in (ItemKind.TEST, ItemKind.APPOINTMENT, ItemKind.TREATMENT) else "9999-12-31")
    return start <= day <= end


def build_checklist(items: list[CarePlanItem], day: str) -> list[ChecklistItem]:
    """Pure function: plan items → today's tickable rows."""
    rows: list[ChecklistItem] = []
    for it in items:
        if not _active_on(it, day):
            continue
        base = f"{it.name} {it.dose}".strip()
        if it.notes:
            base += f" ({it.notes})"
        if it.kind in (ItemKind.MEDICATION, ItemKind.INSTRUCTION):
            if not it.timings:  # "as needed" items are not ticked daily
                continue
            for slot in it.timings:
                rows.append(ChecklistItem(it.id, f"{base} — {slot}", it.kind, slot))
        else:
            rows.append(ChecklistItem(it.id, base, it.kind, ""))
    rows.sort(key=lambda r: (_SLOT_ORDER.get(r.slot, 9), r.label))
    return rows


def get_today_checklist(patient_id: int, day: str | None = None) -> list[ChecklistItem]:
    day = day or date.today().isoformat()
    return build_checklist(db.list_plan_items(patient_id), day)
