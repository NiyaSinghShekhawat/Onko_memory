"""
Load the demo patient into SQLite + Hindsight.  Owner: Shreyan.

    python -m seed.load_seed

⚠️ Set HINDSIGHT_BANK_PREFIX=demo in .env before loading the FINAL demo bank.
   While developing, keep your own prefix (dev-shreyan, ...).
"""

from datetime import date, datetime, timedelta

from core import db, memory
from core.contracts import Entry
from seed import rajesh


def d(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def main() -> None:
    db.init_db()
    p = rajesh.PATIENT
    patient = db.create_patient(p["name"], p["age"], p["diagnosis"])
    bank = memory.ensure_bank(patient)
    db.add_plan_items(patient.id, rajesh.plan_items(d))

    print(f"Patient #{patient.id} {patient.name} → bank '{bank}' (Hindsight {'online' if memory.is_online() else 'OFFLINE'})")
    for i, (offset, hour, source, etype, content) in enumerate(rajesh.ENTRIES, 1):
        ts = datetime.combine(date.today() + timedelta(days=offset), datetime.min.time()).replace(hour=hour)
        memory.save_entry(Entry(patient.id, content, source, etype, ts))
        print(f"  [{i}/{len(rajesh.ENTRIES)}] {ts:%d %b} {etype.value}")
    print("Done. Hindsight builds observations in the background — give it a few minutes before the demo.")


if __name__ == "__main__":
    main()
