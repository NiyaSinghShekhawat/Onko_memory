"""Patient dashboard. Owner: Niya.

Top: Today's log (checklist, mood, symptoms, diary, visit note) → Submit → locked for the day.
Bottom: chatbot.
"""

from datetime import date, datetime

import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))  # find ui_common
import ui_common  # noqa: F401,E402
from ui_common import app_footer, app_header, require_role, setup_page

import streamlit as st

from core import chat, db, memory, schedule
from core.contracts import (
    MOODS, SYMPTOMS, CheckStatus, DailyLog, Entry, EntryType, ItemKind, Role,
)

setup_page("My care")
role, patient = require_role(Role.PATIENT)
today = date.today().isoformat()

app_header("Patient Workspace", patient)

st.markdown(
    f'<div class="hero-title">Good morning, {patient.name.split()[0]} <span class="badge">◌ 28 days remembered</span></div>'
    f'<div class="hero-sub">Let\'s check in for today · {date.today():%A, %d %B}</div>',
    unsafe_allow_html=True,
)

STATUS_LABELS = {CheckStatus.DONE: "✅ Done", CheckStatus.MISSED: "❌ Missed", CheckStatus.LATE: "⏰ Late"}

# ─────────────── Today's log ───────────────
existing = db.get_daily_log(patient.id, today)
st.markdown(
    '<div class="section-title">♢ Today\'s Care</div><div class="section-sub">Based on your approved care plan</div>',
    unsafe_allow_html=True,
)

if existing:
    st.success("✅ Today's log is done. See you tomorrow!")
    with st.expander("What you logged today"):
        for ci in existing.checklist:
            st.write(f"{STATUS_LABELS.get(ci.status, ci.status.value)} — {ci.label}")
        st.write(f"Mood: {existing.mood or '—'} · Symptoms: {', '.join(existing.symptoms) or 'none'}")
        if existing.diary:
            st.write(f"Diary: {existing.diary}")
else:
    checklist = schedule.get_today_checklist(patient.id, today)
    has_appointment = any(c.kind in (ItemKind.APPOINTMENT, ItemKind.TREATMENT) for c in checklist)

    with st.form("daily_log"):
        st.markdown('<span class="badge">TODAY\'S SCHEDULE</span>', unsafe_allow_html=True)
        if not checklist:
            st.caption("Nothing scheduled for today.")
        for i, ci in enumerate(checklist):
            ci.status = st.radio(
                ci.label, list(STATUS_LABELS), format_func=STATUS_LABELS.get,
                horizontal=True, index=None, key=f"ci_{i}",
            ) or CheckStatus.PENDING

        st.markdown('<div class="section-title" style="margin-top:1.2rem">☺ How are you feeling today?</div><div class="section-sub">Daily Reflection</div>', unsafe_allow_html=True)
        mood = st.radio("Mood", MOODS, horizontal=True, index=None, label_visibility="collapsed")
        symptoms = st.pills("Symptoms", SYMPTOMS, selection_mode="multi") or []
        symptom_note = st.text_input("Anything about these symptoms?", placeholder="Nausea started after lunch")

        st.markdown('<div class="section-title" style="margin-top:1.2rem">≡ Anything you\'d like us to remember?</div><div class="section-sub">Add anything about your day that may be useful later. OnKo indexes this so your care team and companion understand your context.</div>', unsafe_allow_html=True)
        diary = st.text_area("Diary", label_visibility="collapsed", placeholder="Anything on your mind today…")

        visit_note = ""
        if has_appointment:
            st.markdown("**4. After your appointment**")
            visit_note = st.text_area("What did the doctor tell you today?")

        submitted = st.form_submit_button("☁  Save today's log", type="primary")

    if submitted:
        log = DailyLog(patient.id, today, checklist, mood or "", list(symptoms), symptom_note,
                       diary.strip(), visit_note.strip(), datetime.now())
        db.save_daily_log(log)
        # Each part becomes its own memory so Hindsight can find patterns per type.
        if checklist:
            lines = "\n".join(f"- {c.label}: {c.status.value}" for c in checklist)
            memory.save_entry(Entry(patient.id, f"Daily check-in for {today}:\n{lines}", role, EntryType.CHECKLIST))
        if mood or symptoms or symptom_note:
            memory.save_entry(Entry(patient.id, f"Mood: {mood or 'not given'}. Symptoms: {', '.join(symptoms) or 'none'}. "
                                    f"{symptom_note}".strip(), role, EntryType.SYMPTOM))
        if log.diary:
            memory.save_entry(Entry(patient.id, log.diary, role, EntryType.DIARY))
        if log.visit_note:
            memory.save_entry(Entry(patient.id, f"Patient's note after appointment: {log.visit_note}", role, EntryType.VISIT_NOTE))
        st.rerun()

# ─────────────── Chatbot ───────────────
st.markdown('<div class="section-title">✣ Ask OnKo <span class="badge">● memory indexed</span></div><div class="section-sub">Ask about appointments, medications, past symptoms, or lab results.</div><div class="memory-note">✦ <b>Using your care memory</b> · OnKo recalls your approved plan and past check-ins.</div>', unsafe_allow_html=True)

history = st.session_state.setdefault("chat_history", [])
for msg in history:
    st.chat_message(msg["role"]).markdown(msg["text"])

if prompt := st.chat_input("e.g. When is my next test?"):
    history.append({"role": "user", "text": prompt})
    st.chat_message("user").markdown(prompt)
    with st.chat_message("assistant"), st.spinner("Thinking…"):
        try:
            reply = chat.handle_message(patient.id, prompt, role)
            (st.error if reply.is_emergency else st.markdown)(reply.text)
            history.append({"role": "assistant", "text": reply.text})
        except Exception as e:
            st.error(f"Something went wrong: {e}")

app_footer()
