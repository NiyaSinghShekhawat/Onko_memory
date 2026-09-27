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
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Manrope:wght@400;500;600;700&display=swap');

:root{
 --primary:#012d1d;--primary-container:#1b4332;--secondary:#396752;
 --secondary-container:#bceed3;--surface:#f3fbf6;--surface-low:#edf6f0;
 --surface-container:#e7f0eb;--surface-high:#e2eae5;--surface-highest:#dce4df;
 --white:#fff;--text:#151d1a;--muted:#414844;--outline:#717973;--outline-soft:#c1c8c2;
 --error:#ba1a1a;--error-bg:#ffdad6;--error-text:#93000a;--late-bg:#ffdcbe;--late-text:#693c00;
}
html,body,[class*="css"],[data-testid="stAppViewContainer"]{font-family:'Manrope',sans-serif!important;color:var(--text)!important}
.stApp{background:var(--surface)!important}
[data-testid="stHeader"]{background:transparent!important}
[data-testid="stSidebar"],[data-testid="collapsedControl"]{display:none!important}
.block-container{max-width:1240px!important;padding:1.25rem 2.5rem 3rem!important}
h1,h2,h3{font-family:'Manrope',sans-serif!important;color:var(--primary)!important}
p,label,.stCaption{color:var(--muted)}
hr{border-color:var(--surface-highest)!important}

/* Stitch type scale */
.hero-title{font:600 36px/44px 'Manrope',sans-serif!important;letter-spacing:-.02em;color:var(--primary);margin:.25rem 0}
.hero-sub{font:400 17px/26px 'Manrope',sans-serif!important;color:var(--muted)}
.section-title{font:600 22px/30px 'Manrope',sans-serif!important;letter-spacing:-.01em;color:var(--primary);margin-bottom:.1rem}
.section-sub{font:400 13px/19px 'Manrope',sans-serif!important;color:var(--muted);margin-bottom:.55rem}
.eyebrow{font:500 12px/16px 'Manrope',sans-serif!important;letter-spacing:.08em;text-transform:uppercase;color:var(--secondary)}
.badge{display:inline-flex;align-items:center;padding:.25rem .65rem;border-radius:999px;background:var(--secondary-container);color:#204f3c;font:500 12px/16px 'Manrope',sans-serif}
.memory-note{background:var(--surface-low);border-radius:8px;padding:.75rem 1rem;color:var(--text);font:400 13px/19px 'Manrope',sans-serif}
.source-chip{display:inline-block;background:var(--surface-low);border-radius:5px;padding:.2rem .45rem;color:var(--secondary);font:500 11px/14px 'JetBrains Mono',monospace}
.mono,code{font-family:'JetBrains Mono',monospace!important}

/* Header */
.onko-top{display:flex;align-items:center;justify-content:space-between;gap:1.5rem;padding:.25rem 0 1rem;border-bottom:1px solid var(--surface-highest);margin-bottom:1.5rem}
.onko-brand{font:600 18px/26px 'Manrope',sans-serif;color:var(--primary)}
.onko-brand small{display:block;font:500 11px/14px 'Manrope',sans-serif;color:var(--muted);margin-top:1px}
.onko-nav{display:flex;gap:.1rem;background:var(--surface-low);border-radius:999px;padding:.25rem}
.onko-nav span{padding:.42rem .85rem;border-radius:999px;font:500 12px/16px 'Manrope',sans-serif;color:var(--muted);white-space:nowrap}
.onko-nav .active{background:var(--secondary-container);color:#204f3c}
.onko-context{display:flex;align-items:center;gap:.5rem;font:500 11px/14px 'Manrope',sans-serif}
.onko-pill{background:#fff;color:var(--text);border-radius:999px;padding:.45rem .7rem;box-shadow:0 1px 4px rgba(27,67,50,.04)}
.onko-memory{display:inline-flex;align-items:center;gap:.35rem;background:var(--surface-container);color:var(--muted);border-radius:999px;padding:.4rem .55rem}
.onko-memory b{background:var(--primary-container);color:#fff!important;border-radius:999px;padding:.18rem .45rem;font-size:11px}

/* Cards */
[data-testid="stVerticalBlockBorderWrapper"]{background:#fff!important;border:0!important;border-radius:12px!important;box-shadow:0 1px 5px rgba(27,67,50,.055)!important}
div[data-testid="stForm"]{background:#fff!important;border:0!important;border-radius:12px!important;padding:1rem!important}
[data-testid="stVerticalBlock"]{gap:.85rem}

/* Buttons */
.stButton>button,.stFormSubmitButton>button{min-height:2.35rem!important;border-radius:8px!important;border:0!important;background:var(--surface-container)!important;color:var(--primary)!important;font:600 14px/20px 'Manrope',sans-serif!important;box-shadow:none!important}
.stButton>button p,.stButton>button span,.stFormSubmitButton>button p,.stFormSubmitButton>button span{color:inherit!important;-webkit-text-fill-color:currentColor!important}
.stButton>button[kind="primary"],.stFormSubmitButton>button[kind="primary"]{background:var(--primary)!important;color:#fff!important}
.stButton>button[kind="primary"]:hover,.stFormSubmitButton>button[kind="primary"]:hover{background:var(--primary-container)!important;color:#fff!important}
.stButton>button:not([kind="primary"]):hover{background:var(--secondary-container)!important;color:#204f3c!important}

/* Inputs/selects */
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div{background:var(--surface-low)!important;color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;border:0!important;border-radius:8px!important;box-shadow:inset 0 1px 2px rgba(21,29,26,.06)!important;font:400 15px/23px 'Manrope',sans-serif!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#66756e!important;-webkit-text-fill-color:#66756e!important;opacity:1!important}
[data-baseweb="select"] span{color:var(--text)!important;-webkit-text-fill-color:var(--text)!important}

/* Patient care status radios: exact Stitch semantic states */
[class*="st-key-ci_"] [role="radiogroup"]{display:flex;gap:.2rem!important;background:#fff;padding:.2rem;border-radius:8px}
[class*="st-key-ci_"] [role="radiogroup"] label{padding:.38rem .7rem!important;border:0!important;border-radius:6px!important;background:#fff!important}
[class*="st-key-ci_"] [role="radiogroup"] label p{color:var(--muted)!important;font:500 12px/16px 'Manrope',sans-serif!important}
[class*="st-key-ci_"] [data-baseweb="radio"]>div:first-child{display:none!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(1):has(input:checked){background:var(--secondary-container)!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(1):has(input:checked) p{color:#204f3c!important;font-weight:600!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(2):has(input:checked){background:var(--error-bg)!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(2):has(input:checked) p{color:var(--error-text)!important;font-weight:600!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(3):has(input:checked){background:var(--late-bg)!important}
[class*="st-key-ci_"] [role="radiogroup"] label:nth-child(3):has(input:checked) p{color:var(--late-text)!important;font-weight:600!important}

/* Mood selector */
.st-key-mood_selector [role="radiogroup"]{display:grid!important;grid-template-columns:repeat(3,1fr);gap:.5rem!important}
.st-key-mood_selector [role="radiogroup"] label{justify-content:center!important;background:var(--surface-low)!important;border:0!important;border-radius:12px!important;padding:.75rem!important}
.st-key-mood_selector [data-baseweb="radio"]>div:first-child{display:none!important}
.st-key-mood_selector [role="radiogroup"] label:has(input:checked){background:var(--secondary-container)!important}
.st-key-mood_selector [role="radiogroup"] label p{color:var(--text)!important;font:500 12px/16px 'Manrope',sans-serif!important}

/* Symptom pills */
[data-testid="stPills"] button{background:var(--surface-container)!important;color:var(--muted)!important;border:0!important;border-radius:999px!important;min-height:1.9rem!important;padding:.3rem .75rem!important}
[data-testid="stPills"] button p,[data-testid="stPills"] button span{color:inherit!important;-webkit-text-fill-color:currentColor!important}
[data-testid="stPills"] button[aria-pressed="true"]{background:var(--secondary-container)!important;color:#204f3c!important;font-weight:600!important}

/* Chat */
[data-testid="stChatMessage"]{background:#fff!important;border:0!important;border-radius:12px!important;padding:.7rem .85rem!important;box-shadow:0 1px 4px rgba(27,67,50,.04)!important}
[data-testid="stChatMessage"] p,[data-testid="stChatMessage"] span{color:var(--text)!important}
[data-testid="stChatInput"]{background:var(--surface-low)!important;border:0!important;border-radius:8px!important}
[data-testid="stChatInput"] textarea{background:transparent!important;color:var(--text)!important;-webkit-text-fill-color:var(--text)!important;font:400 13px/19px 'Manrope',sans-serif!important}
[data-testid="stChatInput"] textarea::placeholder{color:#66756e!important;-webkit-text-fill-color:#66756e!important;opacity:1!important}
[data-testid="stChatInput"] button{background:var(--primary)!important;color:#fff!important}
[data-testid="stChatInput"] button svg{fill:#fff!important;color:#fff!important}

/* Upload / tables / alerts */
[data-testid="stFileUploaderDropzone"]{background:var(--surface-low)!important;border:0!important;border-radius:12px!important}
[data-testid="stMetric"]{background:var(--surface-low)!important;border:0!important;border-radius:8px!important;padding:.65rem .8rem}
.stAlert{border-radius:8px!important;color:var(--text)!important}
.timeline-item{border-left:2px solid var(--secondary-container);padding:.1rem 0 .85rem .8rem;margin-left:.25rem}
.timeline-item b{font:600 14px/20px 'Manrope',sans-serif;color:var(--primary)}
.timeline-item p{font:400 13px/19px 'Manrope',sans-serif;color:var(--muted);margin:.15rem 0}
.onko-footer{display:flex;justify-content:space-between;border-top:1px solid var(--surface-highest);margin-top:2.25rem;padding-top:1rem;color:var(--muted);font:500 11px/14px 'Manrope',sans-serif}

@media(max-width:900px){
 .block-container{padding:1rem 1.25rem 2.5rem!important}
 .onko-nav{display:none}.onko-context{display:none}
 .hero-title{font-size:28px!important;line-height:36px!important}
}
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
