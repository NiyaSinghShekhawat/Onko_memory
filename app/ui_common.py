"""Shared UI helpers for all pages. Owner: Niya."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402
from core import db  # noqa: E402
from core.contracts import Patient, Role  # noqa: E402

CSS = """
<style>
:root{--ink:#123f35;--green:#1f6b57;--mint:#cfe9dc;--soft:#edf5f1;--canvas:#f8fbf9;--line:#d7e4dd;--muted:#61766e}
html,body,[class*="css"]{font-family:"Segoe UI",Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,sans-serif;color:var(--ink);font-size:16px}
.stApp{background:var(--canvas)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{max-width:1280px;padding:1.15rem 2.2rem 3.5rem}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.035em}
h1{font-size:2.35rem!important} h2{font-size:1.65rem!important} h3{font-size:1.25rem!important}
p,label,.stCaption{color:#3e5f55;font-size:.94rem!important;line-height:1.5}
hr{border-color:var(--line)!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line)!important;border-radius:16px!important;box-shadow:0 2px 8px rgba(24,75,60,.045)}
div[data-testid="stForm"]{border:1px solid var(--line);border-radius:13px;background:#fff;padding:1rem}
.stButton>button,.stFormSubmitButton>button{border-radius:8px;min-height:2.25rem;font-weight:600;border:1px solid var(--line)}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--green);color:#fff!important;border-color:var(--green)}
div[data-baseweb="select"]>div,.stTextInput input,.stTextArea textarea{background:#f3f7f5!important;border-color:#ccdcd4!important;border-radius:8px!important}
div[role="radiogroup"]{gap:.25rem}
div[role="radiogroup"] label{background:#f7faf8;border:1px solid #dbe7e1;border-radius:8px;padding:.22rem .5rem}
[data-testid="stFileUploaderDropzone"]{background:#f4f8f6;border:1px dashed #b9d2c6;border-radius:12px}
[data-testid="stChatMessage"]{background:#fff;border:1px solid #e5eee9;border-radius:12px;padding:.55rem .7rem;margin:.45rem 0}
[data-testid="stMetric"]{background:#eef7f2;border:1px solid #e1eee7;padding:.55rem .7rem;border-radius:8px}
.stAlert{border-radius:9px}
.onko-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.15rem 0 .8rem;border-bottom:1px solid #e4f0e9;margin-bottom:1.2rem}
.onko-brand{font-weight:700;font-size:1.2rem;color:var(--ink)} .onko-brand small{display:block;font-weight:400;font-size:.72rem;color:var(--muted);margin-top:.12rem}
.onko-nav{display:flex;gap:.15rem;background:#edf5f0;border-radius:999px;padding:.2rem}
.onko-nav span{padding:.5rem .85rem;border-radius:999px;font-size:.78rem;color:#4c685e;white-space:nowrap}.onko-nav .active{background:var(--mint);color:#184c3d}.onko-nav{background:#eef4f1}
.onko-context{display:flex;align-items:center;gap:.4rem;font-size:.75rem}.onko-pill{background:#fff;border:1px solid #e5efe9;border-radius:999px;padding:.4rem .65rem}.onko-memory{background:#e8f1ed;border-radius:999px;padding:.4rem .65rem}.onko-memory b{background:#07533d;color:#fff;border-radius:999px;padding:.08rem .32rem}
.eyebrow{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;color:#5b776d;font-weight:600}.hero-title{font-size:2.4rem;font-weight:700;letter-spacing:-.045em;line-height:1.08;margin:.3rem 0;color:var(--ink)}.hero-sub{font-size:1rem;color:#586f66;line-height:1.55}
.section-title{font-size:1.3rem;font-weight:700;color:var(--ink);margin-bottom:.1rem}.section-sub{font-size:.88rem;color:#60766d;margin-bottom:.75rem;line-height:1.45}
.badge{display:inline-block;padding:.25rem .55rem;border-radius:999px;background:#e3f0e9;color:#356454;font-size:.72rem}.memory-note{background:#e8f1ed;border-radius:8px;padding:.6rem .7rem;font-size:.84rem;color:#315c4b;line-height:1.45}.source-chip{display:inline-block;background:#eaf5ef;border-radius:5px;padding:.18rem .4rem;font:500 .7rem monospace;color:#315d4b;margin-top:.3rem}
.timeline-item{border-left:2px solid #a8d9bf;padding:.15rem 0 .7rem .7rem;margin-left:.2rem}.timeline-item b{font-size:.88rem}.timeline-item p{font-size:.82rem;margin:.15rem 0}
.onko-footer{display:flex;justify-content:space-between;border-top:1px solid #e3efe8;margin-top:2.2rem;padding-top:1rem;color:#587268;font-size:.72rem}
@media(max-width:800px){.block-container{padding:1rem 1rem 3rem}.onko-nav,.onko-context{display:none}.hero-title{font-size:1.6rem}}
</style>
"""


def setup_page(title: str) -> None:
    st.set_page_config(page_title=f"OnKo Memory · {title}", page_icon="✣", layout="wide", initial_sidebar_state="collapsed")
    db.init_db()
    st.markdown(CSS, unsafe_allow_html=True)


def app_header(active: str = "Role Selection", patient: Patient | None = None) -> None:
    patient_html = ""
    if patient is not None:
        patient_html = f'<span class="onko-pill">● &nbsp;{patient.name} &nbsp;<small>({patient.id})</small></span>'
    st.markdown(f'''<div class="onko-top">
      <div class="onko-brand">OnKo Memory<small>Your care journey, remembered.</small></div>
      <div class="onko-nav">
        <span class="{'active' if active == 'Role Selection' else ''}">Role Selection</span>
        <span class="{'active' if active == 'Patient Workspace' else ''}">Patient Workspace</span>
        <span class="{'active' if active == 'Doctor / Nurse Workspace' else ''}">Doctor / Nurse Workspace</span>
      </div>
      <div class="onko-context">{patient_html}<span class="onko-memory">Care Memory: <b>ON</b></span></div>
    </div>''', unsafe_allow_html=True)


def app_footer() -> None:
    st.markdown('<div class="onko-footer"><span><b>OnKo Memory</b> &nbsp;·&nbsp; Longitudinal AI Oncology Support</span><span>● Privacy-first care memory &nbsp;&nbsp; © 2026 OnKo</span></div>', unsafe_allow_html=True)


def require_role(*roles: Role) -> tuple[Role, Patient]:
    role = st.session_state.get("role")
    patient = st.session_state.get("patient")
    if role not in roles or patient is None:
        allowed = " / ".join(r.value.title() for r in roles)
        st.warning(f"Please go to **Home** and sign in as {allowed} with a patient selected.")
        st.stop()
    return role, patient

