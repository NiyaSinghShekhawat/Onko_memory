"""Home: pick role + patient (simple demo login). Owner: Niya."""

import ui_common  # noqa: F401  (must be first: fixes import path)
from ui_common import setup_page

import streamlit as st

from core import config, db, memory
from core.contracts import Role

setup_page("Home")

st.title("🩺 OnKo")
st.caption("The doctor decides the care. OnKo remembers the journey.")

patients = db.list_patients()

if not patients:
    st.info("No patients yet. Load the demo patient (`python -m seed.load_seed`) or create one below.")

with st.expander("➕ Create a patient", expanded=not patients):
    with st.form("new_patient"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, value=50)
        diagnosis = st.text_input("Diagnosis", placeholder="e.g. Colon cancer, on CAPOX")
        if st.form_submit_button("Create") and name.strip():
            p = db.create_patient(name.strip(), int(age), diagnosis.strip())
            memory.ensure_bank(p)
            st.success(f"Created {p.name}")
            st.rerun()

if patients:
    st.subheader("Sign in")
    role = st.radio("I am a…", list(Role), format_func=lambda r: r.value.title(), horizontal=True)
    patient = st.selectbox("Patient", patients, format_func=lambda p: f"{p.name} · {p.diagnosis}")
    if st.button("Continue", type="primary"):
        st.session_state.role = role
        st.session_state.patient = patient
        memory.ensure_bank(patient)
        st.switch_page("pages/2_Patient.py" if role == Role.PATIENT else "pages/1_Doctor.py")

st.divider()
c1, c2 = st.columns(2)
c1.metric("Hindsight", "online" if memory.is_online() else "offline (fallback)")
c2.metric("Groq", "stub mode" if config.USE_STUBS else ("key set" if config.GROQ_API_KEY else "no key"))
