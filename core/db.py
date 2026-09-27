"""
SQLite storage for app logic (NOT memory). Owner: Samprada.

Holds: patients, the approved care-plan schedule, daily-log lock status,
and when the doctor last reviewed each patient. Everything the chatbot
"remembers" lives in Hindsight (core/memory.py), not here.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime

from core import config
from core.contracts import (
    CarePlanItem, CheckStatus, ChecklistItem, DailyLog, ItemKind, Patient,
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER,
    diagnosis TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    name TEXT NOT NULL,
    dose TEXT DEFAULT '',
    timings TEXT DEFAULT '[]',
    start_date TEXT DEFAULT '',
    end_date TEXT DEFAULT '',
    notes TEXT DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS daily_logs (
    patient_id INTEGER NOT NULL,
    day TEXT NOT NULL,
    payload TEXT NOT NULL,
    submitted_at TEXT NOT NULL,
    PRIMARY KEY (patient_id, day)
);
CREATE TABLE IF NOT EXISTS reviews (
    patient_id INTEGER PRIMARY KEY,
    reviewed_at TEXT NOT NULL
);
"""


def _conn() -> sqlite3.Connection:
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _conn() as c:
        c.executescript(_SCHEMA)


# ─────────────── Patients ───────────────

def create_patient(name: str, age: int | None, diagnosis: str) -> Patient:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO patients (name, age, diagnosis) VALUES (?, ?, ?)",
            (name, age, diagnosis),
        )
        return Patient(id=cur.lastrowid, name=name, age=age, diagnosis=diagnosis)


def list_patients() -> list[Patient]:
    with _conn() as c:
        rows = c.execute("SELECT * FROM patients ORDER BY id").fetchall()
    return [Patient(id=r["id"], name=r["name"], age=r["age"], diagnosis=r["diagnosis"]) for r in rows]


def get_patient(patient_id: int) -> Patient | None:
    with _conn() as c:
        r = c.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    return Patient(id=r["id"], name=r["name"], age=r["age"], diagnosis=r["diagnosis"]) if r else None


# ─────────────── Care plan ───────────────

def add_plan_items(patient_id: int, items: list[CarePlanItem]) -> list[CarePlanItem]:
    """Save doctor-APPROVED items. Returns the items with their new ids."""
    saved: list[CarePlanItem] = []
    now = datetime.now().isoformat(timespec="seconds")
    with _conn() as c:
        for it in items:
            cur = c.execute(
                """INSERT INTO plan_items
                   (patient_id, kind, name, dose, timings, start_date, end_date, notes, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (patient_id, ItemKind(it.kind).value, it.name, it.dose,
                 json.dumps(it.timings), it.start_date, it.end_date, it.notes, now),
            )
            saved.append(CarePlanItem(**{**asdict(it), "kind": ItemKind(it.kind), "id": cur.lastrowid}))
    return saved


def list_plan_items(patient_id: int) -> list[CarePlanItem]:
    with _conn() as c:
        rows = c.execute(
            "SELECT * FROM plan_items WHERE patient_id = ? ORDER BY start_date, id", (patient_id,)
        ).fetchall()
    return [
        CarePlanItem(
            id=r["id"], kind=ItemKind(r["kind"]), name=r["name"], dose=r["dose"],
            timings=json.loads(r["timings"] or "[]"), start_date=r["start_date"],
            end_date=r["end_date"], notes=r["notes"],
        )
        for r in rows
    ]


# ─────────────── Daily logs ───────────────

def save_daily_log(log: DailyLog) -> None:
    submitted = log.submitted_at or datetime.now()
    payload = asdict(log)
    payload["submitted_at"] = submitted.isoformat(timespec="seconds")
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO daily_logs (patient_id, day, payload, submitted_at) VALUES (?, ?, ?, ?)",
            (log.patient_id, log.day, json.dumps(payload, default=str), payload["submitted_at"]),
        )


def get_daily_log(patient_id: int, day: str) -> DailyLog | None:
    """Returns the log if already submitted for that day (→ form is locked)."""
    with _conn() as c:
        r = c.execute(
            "SELECT payload FROM daily_logs WHERE patient_id = ? AND day = ?", (patient_id, day)
        ).fetchone()
    if not r:
        return None
    p = json.loads(r["payload"])
    p["checklist"] = [
        ChecklistItem(**{**ci, "kind": ItemKind(ci["kind"]), "status": CheckStatus(ci["status"])})
        for ci in p["checklist"]
    ]
    p["submitted_at"] = datetime.fromisoformat(p["submitted_at"])
    return DailyLog(**p)


# ─────────────── Doctor reviews ───────────────

def mark_reviewed(patient_id: int, when: datetime | None = None) -> None:
    when = when or datetime.now()
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO reviews (patient_id, reviewed_at) VALUES (?, ?)",
            (patient_id, when.isoformat(timespec="seconds")),
        )


def last_reviewed(patient_id: int) -> datetime | None:
    with _conn() as c:
        r = c.execute("SELECT reviewed_at FROM reviews WHERE patient_id = ?", (patient_id,)).fetchone()
    return datetime.fromisoformat(r["reviewed_at"]) if r else None
