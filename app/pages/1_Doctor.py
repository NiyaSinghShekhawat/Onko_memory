"""Doctor / Nurse workspace — Stitch-matched frontend. Owner: Niya."""
from datetime import date
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import streamlit as st
from ui_common import app_footer, app_header, require_role, setup_page
from core import chat, db, memory
from core.ai.extract import extract_care_plan
from core.ai.pdf import extract_report, read_pdf_text
from core.contracts import TIME_SLOTS, CarePlanItem, Entry, EntryType, ItemKind, ReportValue, Role

setup_page("Doctor / Nurse Workspace")
role, patient = require_role(Role.DOCTOR, Role.NURSE)
app_header("Doctor / Nurse Workspace", patient)

st.markdown(
    f'<div class="section-title">● {patient.name} <span class="badge">Age: {patient.age}</span> '
    f'<span class="badge">{patient.id}</span></div>'
    f'<div class="section-sub">◆ Protocol: {patient.diagnosis or "Active care plan"} &nbsp; · &nbsp; signed in as {role.value}</div>',
    unsafe_allow_html=True,
)

work_col, memory_col = st.columns([1.2, 1], gap="large")

with work_col:
    with st.container(border=True):
        st.markdown('<div class="section-title">▱ Update Care Plan <span class="badge">NATURAL LANG</span></div><div class="section-sub">Enter the plan naturally. OnKo structures it for review before anything is saved.</div>', unsafe_allow_html=True)
        plan_text = st.text_area("Care plan", height=130, label_visibility="collapsed", placeholder="Capecitabine 1500mg twice daily after food, days 1–14. CBC on 3 Oct. Cycle 5 on 10 Oct.")
        if st.button("Structure Care Plan ✦", disabled=not plan_text.strip(), use_container_width=True):
            try:
                with st.spinner("Structuring the plan…"):
                    items = extract_care_plan(plan_text, date.today().isoformat())
                st.session_state.draft_plan = pd.DataFrame([{**i.__dict__, "kind": i.kind.value, "timings": ", ".join(i.timings)} for i in items]).drop(columns=["id"], errors="ignore")
            except Exception as e:
                st.error(f"Extraction failed: {e}")

        if "draft_plan" in st.session_state:
            st.markdown('<div class="memory-note">⬟ <b>Review required</b> · Nothing enters patient memory until you approve it.</div>', unsafe_allow_html=True)
            edited = st.data_editor(
                st.session_state.draft_plan, num_rows="dynamic", width="stretch",
                column_config={
                    "kind": st.column_config.SelectboxColumn("Type", options=[k.value for k in ItemKind], required=True),
                    "timings": st.column_config.TextColumn("Timings", help=f"Comma-separated: {', '.join(TIME_SLOTS)}"),
                }, key="plan_editor",
            )
            if st.button("◉ Approve & Add to Care Memory", type="primary", use_container_width=True):
                approved = [
                    CarePlanItem(
                        kind=ItemKind(r["kind"]), name=str(r["name"]), dose=str(r.get("dose") or ""),
                        timings=[t.strip() for t in str(r.get("timings") or "").split(",") if t.strip() in TIME_SLOTS],
                        start_date=str(r.get("start_date") or ""), end_date=str(r.get("end_date") or ""),
                        notes=str(r.get("notes") or ""),
                    ) for r in edited.to_dict("records") if str(r.get("name") or "").strip()
                ]
                db.add_plan_items(patient.id, approved)
                summary = "\n".join(f"- {i.kind.value}: {i.name} {i.dose} {'/'.join(i.timings)} {i.start_date} {i.notes}".strip() for i in approved)
                memory.save_entry(Entry(patient.id, f"Doctor-approved care plan items:\n{summary}", role, EntryType.CARE_PLAN))
                del st.session_state.draft_plan
                st.success(f"Saved {len(approved)} items.")

        with st.expander("Current approved care plan"):
            current = db.list_plan_items(patient.id)
            if current:
                st.dataframe(pd.DataFrame([{**i.__dict__, "kind": i.kind.value} for i in current]), width="stretch", hide_index=True)
            else:
                st.caption("No approved items yet.")

    with st.container(border=True):
        st.markdown('<div class="section-title">⇧ Add Medical Document</div><div class="section-sub">Drop a PDF here. Extracted values remain in review until confirmation.</div>', unsafe_allow_html=True)
        pdf = st.file_uploader("Medical PDF", type=["pdf"], label_visibility="collapsed")
        if pdf and st.button("◌ Read document", use_container_width=True):
            try:
                with st.spinner("Reading document…"):
                    st.session_state.draft_report = extract_report(read_pdf_text(pdf.getvalue()))
            except Exception as e:
                st.error(f"Could not read the report: {e}")
        rep = st.session_state.get("draft_report")
        if rep:
            c1, c2 = st.columns(2)
            name = c1.text_input("Report", rep.report_name)
            rdate = c2.text_input("Report date", rep.report_date)
            vals = st.data_editor(pd.DataFrame([v.__dict__ for v in rep.values] or [{"name":"","value":"","unit":""}]), num_rows="dynamic", width="stretch", key="report_editor")
            if st.button("✓ Confirm & Save to Memory", type="primary", use_container_width=True):
                values = [ReportValue(**r) for r in vals.to_dict("records") if str(r.get("name") or "").strip()]
                text = f"{name} ({rdate or 'date not given'}): " + ", ".join(f"{v.name} {v.value} {v.unit}".strip() for v in values)
                memory.save_entry(Entry(patient.id, text, role, EntryType.REPORT, metadata={"report": name}))
                del st.session_state.draft_report
                st.success("Document added to care memory.")

    with st.container(border=True):
        st.markdown('<div class="section-title">▤ Add Care Note</div><div class="section-sub">Contextual nuances that may be useful during future interactions.</div>', unsafe_allow_html=True)
        with st.form("notes", clear_on_submit=True):
            note = st.text_area("Care note", label_visibility="collapsed", placeholder="e.g. Patient prefers shorter explanations. Daughter accompanies patient to appointments.")
            if st.form_submit_button("Save Note", use_container_width=True) and note.strip():
                memory.save_entry(Entry(patient.id, note.strip(), role, EntryType.DOCTOR_NOTE))
                st.success("Note saved.")

with memory_col:
    with st.container(border=True):
        last = db.last_reviewed(patient.id)
        st.markdown('<span class="badge">LONGITUDINAL MEMORY SYNTHESIS</span><div class="section-title" style="margin-top:.55rem">≡ Since Last Visit</div><div class="section-sub">A factual view of what has been recorded since the last clinical review.</div>', unsafe_allow_html=True)
        st.caption(f"Last reviewed: {last:%d %b %Y, %I:%M %p}" if last else "Not reviewed yet · showing the last 30 days")
        if st.button("↻ Generate Memory Summary", type="primary", use_container_width=True):
            with st.spinner("Reading this patient's care memory…"):
                st.session_state.summary = chat.since_last_visit(patient.id)

        if st.session_state.get("summary"):
            st.markdown('<div class="memory-note">✦ <b>Memory summary</b> · sourced from recorded patient and care-team entries.</div>', unsafe_allow_html=True)
            st.markdown(st.session_state.summary)
            st.markdown('<div class="source-chip">HINDSIGHT · LONGITUDINAL MEMORY</div>', unsafe_allow_html=True)
            if st.button("✓ Mark as reviewed", use_container_width=True):
                db.mark_reviewed(patient.id)
                st.session_state.pop("summary")
                st.rerun()
        else:
            st.markdown(
                '<div class="timeline-item"><b>Daily activity</b><p>Patient logs, medicine statuses, and check-ins will appear here.</p></div>'
                '<div class="timeline-item"><b>Patient reported</b><p>Symptoms and diary entries are recalled with dates.</p></div>'
                '<div class="timeline-item"><b>Documents</b><p>Confirmed report values are included without interpretation.</p></div>'
                '<div class="timeline-item"><b>Questions asked</b><p>Relevant care questions and SOS events remain part of the longitudinal record.</p></div>',
                unsafe_allow_html=True,
            )

    with st.container(border=True):
        st.markdown('<div class="section-title">✣ Memory Demo</div><div class="section-sub">Persistent memory is the core of this prototype.</div>', unsafe_allow_html=True)
        st.markdown('<div class="memory-note"><b>Care Memory · ON</b><br>OnKo can use this patient\'s previous approved information and interactions.</div>', unsafe_allow_html=True)
        st.caption("Development testing should use the developer memory bank; keep the seeded demo patient clean.")

app_footer()
