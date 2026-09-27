"""Shared UI helpers for all pages. Owner: Niya."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:  # lets pages `import core...` when run via `streamlit run app/Home.py`
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from core import db  # noqa: E402
from core.contracts import Patient, Role  # noqa: E402


def setup_page(title: str) -> None:
    st.set_page_config(page_title=f"OnKo · {title}", page_icon="🩺", layout="centered")
    db.init_db()


def require_role(*roles: Role) -> tuple[Role, Patient]:
    """Stop the page unless the user picked an allowed role + patient on Home."""
    role = st.session_state.get("role")
    patient = st.session_state.get("patient")
    if role not in roles or patient is None:
        allowed = " / ".join(r.value.title() for r in roles)
        st.warning(f"Please go to **Home** and sign in as {allowed} with a patient selected.")
        st.stop()
    return role, patient
