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
:root{--ink:#012d1d;--green:#012d1d;--mint:#bceed3;--soft:#edf6f0;--canvas:#f3fbf6;--line:#dce4df;--muted:#414844;--error:#93000a;--error-bg:#ffdad6;--late:#693c00;--late-bg:#ffdcbe}
html,body,[class*="css"]{font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:var(--ink)}
.stApp{background:var(--canvas)}
[data-testid="stHeader"]{background:transparent}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none}
.block-container{max-width:1320px;padding:1rem 2.2rem 3.5rem}
h1,h2,h3{color:var(--ink)!important;letter-spacing:-.035em}
h1{font-size:2rem!important} h2{font-size:1.35rem!important} h3{font-size:1.05rem!important}
p,label,.stCaption{color:#35584c}
hr{border-color:var(--line)!important}
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff;border:1px solid var(--line)!important;border-radius:13px!important;box-shadow:0 1px 2px rgba(0,58,40,.035)}
div[data-testid="stForm"]{border:1px solid var(--line);border-radius:13px;background:#fff;padding:1rem}
.stButton>button,.stFormSubmitButton>button{border-radius:8px;min-height:2.25rem;font-weight:600;border:1px solid var(--line)}
.stButton>button,.stFormSubmitButton>button{color:var(--ink)!important;background:#e7f0eb!important}
.stButton>button p,.stButton>button span,.stFormSubmitButton>button p,.stFormSubmitButton>button span{color:var(--ink)!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--green)!important;color:#fff!important;border-color:var(--green)!important}
.stButton>button[kind="primary"] p,.stButton>button[kind="primary"] span,.stFormSubmitButton>button[kind="primary"] p,.stFormSubmitButton>button[kind="primary"] span{color:#fff!important}
div[data-baseweb="select"]>div,.stTextInput input,.stTextArea textarea{background:#eef7f2!important;border-color:var(--line)!important;border-radius:8px!important;color:#151d1a!important;-webkit-text-fill-color:#151d1a!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#66756e!important;opacity:1!important}
div[role="radiogroup"]{gap:.25rem}
div[role="radiogroup"] label{background:#f4f8f6;border:1px solid #e6efe9;border-radius:8px;padding:.22rem .5rem;color:#151d1a!important}
div[role="radiogroup"] label p,div[role="radiogroup"] label span{color:#151d1a!important}
div[role="radiogroup"] label:has(input:checked){background:var(--mint)!important;border-color:#8cc8aa!important}
div[role="radiogroup"] label:has(input:checked) p,div[role="radiogroup"] label:has(input:checked) span{color:#204f3c!important;font-weight:700!important}
[data-testid="stPills"] button{background:#e7f0eb!important;border:1px solid #c1c8c2!important}
[data-testid="stPills"] button p,[data-testid="stPills"] button span{color:#151d1a!important}
[data-testid="stPills"] button[aria-pressed="true"]{background:var(--mint)!important;border-color:#8cc8aa!important}
[data-testid="stPills"] button[aria-pressed="true"] p,[data-testid="stPills"] button[aria-pressed="true"] span{color:#204f3c!important;font-weight:600!important}
[data-testid="stFileUploaderDropzone"]{background:#eef7f2;border:1px dashed #b8d5c7;border-radius:12px}
[data-testid="stChatMessage"]{background:#fff;border:1px solid #e5eee9;border-radius:12px;padding:.55rem .7rem;margin:.45rem 0}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] span{color:#151d1a!important}
[data-testid="stChatInput"] textarea{color:#151d1a!important;-webkit-text-fill-color:#151d1a!important}
[data-testid="stChatInput"] textarea::placeholder{color:#66756e!important;opacity:1!important}
[data-testid="stChatInput"] button{background:var(--green)!important;color:#fff!important}
[data-testid="stChatInput"] button svg{fill:#fff!important}
[data-testid="stToggle"] label,[data-testid="stToggle"] p,[data-testid="stToggle"] span{color:#151d1a!important;opacity:1!important}
[data-testid="stToggle"] [role="switch"][aria-checked="true"]{background:var(--green)!important}
[data-testid="stMetric"]{background:#eef7f2;border:1px solid #e1eee7;padding:.55rem .7rem;border-radius:8px}
.stAlert{border-radius:9px}
.onko-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.15rem 0 .8rem;border-bottom:1px solid #e4f0e9;margin-bottom:1.2rem}
.onko-brand{font-weight:700;font-size:1.05rem;color:var(--ink)} .onko-brand small{display:block;font-weight:400;font-size:.6rem;color:var(--muted);margin-top:.12rem}
.onko-nav{display:flex;gap:.15rem;background:#edf5f0;border-radius:999px;padding:.2rem}
.onko-nav span{padding:.4rem .75rem;border-radius:999px;font-size:.7rem;color:#4c685e;white-space:nowrap}.onko-nav .active{background:var(--mint);color:#255b47}
.onko-context{display:flex;align-items:center;gap:.4rem;font-size:.65rem}.onko-pill{background:#fff;border:1px solid #e5efe9;border-radius:999px;padding:.4rem .65rem}.onko-memory{background:#e7f3ec;border-radius:999px;padding:.4rem .65rem}.onko-memory b{background:#07533d;color:#fff;border-radius:999px;padding:.08rem .32rem}
.eyebrow{font-size:.62rem;letter-spacing:.1em;text-transform:uppercase;color:#5b776d;font-weight:600}.hero-title{font-size:2rem;font-weight:700;letter-spacing:-.045em;line-height:1.08;margin:.3rem 0;color:var(--ink)}.hero-sub{font-size:.82rem;color:#586f66}
.section-title{font-size:1.05rem;font-weight:700;color:var(--ink);margin-bottom:.1rem}.section-sub{font-size:.7rem;color:#60766d;margin-bottom:.65rem}
.badge{display:inline-block;padding:.2rem .5rem;border-radius:999px;background:#e4f5eb;color:#39705b;font-size:.6rem}.memory-note{background:#e9f4ee;border-radius:8px;padding:.6rem .7rem;font-size:.69rem;color:#315c4b}.source-chip{display:inline-block;background:#eaf5ef;border-radius:5px;padding:.18rem .4rem;font:500 .6rem monospace;color:#315d4b;margin-top:.3rem}
.timeline-item{border-left:2px solid #a8d9bf;padding:.15rem 0 .7rem .7rem;margin-left:.2rem}.timeline-item b{font-size:.7rem}.timeline-item p{font-size:.68rem;margin:.15rem 0}
.onko-footer{display:flex;justify-content:space-between;border-top:1px solid #e3efe8;margin-top:2.2rem;padding-top:1rem;color:#587268;font-size:.62rem}
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
