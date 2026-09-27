"""Doctor / Nurse dashboard. Owner: Niya.

1. Care plan text → AI extract → edit table → Approve (only then saved)
2. PDF report upload → extract → edit → Confirm
3. Additional notes
4. "Since last visit" summary
"""

from datetime import date

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # find ui_common
import ui_common  # noqa: F401,E402
from ui_common import require_role, setup_page

import pandas as pd
import streamlit as st

from core import chat, db, memory
from core.ai.extract import extract_care_plan
from core.ai.pdf import extract_report, read_pdf_text
from core.contracts import TIME_SLOTS, CarePlanItem, Entry, EntryType, ItemKind, ReportValue, Role

setup_page("Care team")
role, patient = require_role(Role.DOCTOR, Role.NURSE)

st.title(f"👩‍⚕️ {patient.name}")
st.caption(f"{patient.diagnosis} · signed in as {role.value}")

tab_plan, tab_report, tab_notes, tab_summary = st.tabs(
    ["📋 Care plan", "📄 Reports", "📝 Notes", "🕑 Since last visit"]
)

# ─────────────── 1. Care plan ───────────────
with tab_plan:
    st.subheader("Enter the care plan")
    plan_text = st.text_area(
        "Medicines, tests, treatments, appointments",
        height=150,
        placeholder="Capecitabine 1500mg twice daily after food, days 1–14. "
                    "Ondansetron 8mg if nausea. CBC on 3 Oct. Review on 10 Oct.",
    )
    if st.button("✨ Extract", disabled=not plan_text.strip()):
        try:
            with st.spinner("Structuring the plan…"):
                items = extract_care_plan(plan_text, date.today().isoformat())
            st.session_state.draft_plan = pd.DataFrame([
                {**i.__dict__, "kind": i.kind.value, "timings": ", ".join(i.timings)} for i in items
            ]).drop(columns=["id"], errors="ignore")
        except Exception as e:
            st.error(f"Extraction failed: {e}")

    if "draft_plan" in st.session_state:
        st.caption("Review and edit. Nothing is saved until you approve.")
        edited = st.data_editor(
            st.session_state.draft_plan,
            num_rows="dynamic",
            width="stretch",
            column_config={
                "kind": st.column_config.SelectboxColumn("Kind", options=[k.value for k in ItemKind], required=True),
                "timings": st.column_config.TextColumn("Timings", help=f"Comma-separated: {', '.join(TIME_SLOTS)}"),
            },
            key="plan_editor",
        )
        if st.button("✅ Approve & save", type="primary"):
            approved = [
                CarePlanItem(
                    kind=ItemKind(r["kind"]), name=str(r["name"]), dose=str(r.get("dose") or ""),
                    timings=[t.strip() for t in str(r.get("timings") or "").split(",") if t.strip() in TIME_SLOTS],
                    start_date=str(r.get("start_date") or ""), end_date=str(r.get("end_date") or ""),
                    notes=str(r.get("notes") or ""),
                )
                for r in edited.to_dict("records") if str(r.get("name") or "").strip()
            ]
            db.add_plan_items(patient.id, approved)
            summary = "\n".join(
                f"- {i.kind.value}: {i.name} {i.dose} {('/'.join(i.timings))} "
                f"{i.start_date}{' to ' + i.end_date if i.end_date else ''} {i.notes}".strip()
                for i in approved
            )
            memory.save_entry(Entry(patient.id, f"Doctor-approved care plan items:\n{summary}", role, EntryType.CARE_PLAN))
            del st.session_state.draft_plan
            st.success(f"Saved {len(approved)} items.")

    with st.expander("Current care plan"):
        current = db.list_plan_items(patient.id)
        if current:
            st.dataframe(pd.DataFrame([{**i.__dict__, "kind": i.kind.value} for i in current]), width="stretch")
        else:
            st.write("No items yet.")

# ─────────────── 2. Reports ───────────────
with tab_report:
    st.subheader("Upload a report (PDF)")
    pdf = st.file_uploader("PDF", type=["pdf"])
    if pdf and st.button("🔍 Read report"):
        try:
            with st.spinner("Reading…"):
                st.session_state.draft_report = extract_report(read_pdf_text(pdf.getvalue()))
        except Exception as e:
            st.error(f"Could not read the report: {e}")

    rep = st.session_state.get("draft_report")
    if rep:
        c1, c2 = st.columns(2)
        name = c1.text_input("Report", rep.report_name)
        rdate = c2.text_input("Report date", rep.report_date)
        vals = st.data_editor(
            pd.DataFrame([v.__dict__ for v in rep.values] or [{"name": "", "value": "", "unit": ""}]),
            num_rows="dynamic", width="stretch", key="report_editor",
        )
        if st.button("✅ Confirm & save", type="primary"):
            values = [ReportValue(**r) for r in vals.to_dict("records") if str(r.get("name") or "").strip()]
            text = f"{name} ({rdate or 'date not given'}): " + ", ".join(f"{v.name} {v.value} {v.unit}".strip() for v in values)
            memory.save_entry(Entry(patient.id, text, role, EntryType.REPORT, metadata={"report": name}))
            del st.session_state.draft_report
            st.success("Report saved.")

# ─────────────── 3. Notes ───────────────
with tab_notes:
    st.subheader("Additional information")
    with st.form("notes", clear_on_submit=True):
        note = st.text_area("Note", placeholder="e.g. Patient anxious about hair loss. Family prefers Telugu.")
        if st.form_submit_button("Save note") and note.strip():
            memory.save_entry(Entry(patient.id, note.strip(), role, EntryType.DOCTOR_NOTE))
            st.success("Note saved.")

# ─────────────── 4. Since last visit ───────────────
with tab_summary:
    last = db.last_reviewed(patient.id)
    st.subheader("Since last visit")
    st.caption(f"Last reviewed: {last:%d %b %Y, %I:%M %p}" if last else "Not reviewed yet (showing last 30 days).")
    if st.button("🧠 Generate summary"):
        with st.spinner("Reading this patient's memory…"):
            st.session_state.summary = chat.since_last_visit(patient.id)
    if st.session_state.get("summary"):
        st.markdown(st.session_state.summary)
        if st.button("Mark as reviewed"):
            db.mark_reviewed(patient.id)
            st.session_state.pop("summary")
            st.rerun()
