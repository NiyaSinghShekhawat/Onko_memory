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
    st.markdown(CALIBRATION_CSS, unsafe_allow_html=True)


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




CALIBRATION_CSS = """
<style>
/* Visual calibration against the Stitch reference */
html,body,[class*="css"]{font-family:Inter,"Aptos","Segoe UI",sans-serif!important;font-size:15px!important}
.stApp{background:#f4faf6!important}
.block-container{max-width:1220px!important;padding-top:.65rem!important}
.onko-top{padding:.15rem 0 .65rem!important;margin-bottom:1rem!important}
.onko-brand{font-size:1.05rem!important;letter-spacing:-.02em}
.onko-brand small{font-size:.62rem!important}
.onko-nav span{font-size:.68rem!important;padding:.38rem .72rem!important}
.onko-context{font-size:.64rem!important}
.hero-title{font-size:2rem!important;line-height:1.08!important;font-weight:700!important;letter-spacing:-.045em!important;margin-top:.55rem!important}
.hero-title .badge{vertical-align:middle;margin-left:.4rem}
.hero-sub{font-size:.82rem!important;line-height:1.45!important}
.section-title{font-size:1.08rem!important;line-height:1.25!important;font-weight:700!important;letter-spacing:-.02em!important}
.section-sub{font-size:.7rem!important;line-height:1.4!important;color:#657c73!important}
.badge{font-size:.6rem!important;padding:.2rem .48rem!important}
.memory-note{font-size:.7rem!important;line-height:1.45!important;background:#e7f2ec!important}
.source-chip{font-size:.58rem!important}
p,label,.stCaption{font-size:.75rem!important;line-height:1.42!important}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:12px!important;box-shadow:none!important;border-color:#d8e7df!important}
div[data-testid="stForm"]{padding:.75rem!important;border-radius:12px!important}
.stButton>button,.stFormSubmitButton>button{font-size:.72rem!important;min-height:2rem!important;border-radius:7px!important}
/* Match Stitch: secondary actions are pale, not black */
.stButton>button[kind="secondary"]{background:#f2f7f4!important;color:#315b4d!important;border:1px solid #d8e6df!important}
.stButton>button[kind="secondary"]:hover{background:#e5f2eb!important;border-color:#bad8c9!important;color:#174c3b!important}
/* Segmented radio controls: remove Streamlit's heavy black dot */
div[role="radiogroup"]{gap:.3rem!important}
div[role="radiogroup"] label{background:#f5f9f7!important;border:1px solid #d9e6df!important;border-radius:7px!important;padding:.28rem .52rem!important}
div[role="radiogroup"] label:has(input:checked){background:#bdebd4!important;border-color:#bdebd4!important;color:#174c3b!important}
div[role="radiogroup"] [data-testid="stMarkdownContainer"] p{font-size:.72rem!important}
div[role="radiogroup"] div[data-testid="stRadio"]{gap:.2rem}
div[role="radiogroup"] [data-baseweb="radio"]>div:first-child{display:none!important}
/* Symptom chips should be soft mint like the reference, never dark */
[data-testid="stPills"] button{background:#e3f3ea!important;color:#356454!important;border:1px solid #d1e9dc!important;font-size:.68rem!important;min-height:1.7rem!important;padding:.2rem .55rem!important}
[data-testid="stPills"] button[aria-pressed="true"]{background:#aee9ca!important;color:#174c3b!important;border-color:#aee9ca!important}
/* Inputs and chat are pale green in Stitch */
.stTextInput input,.stTextArea textarea{background:#edf5f1!important;color:#274e42!important;font-size:.75rem!important}
[data-testid="stChatInput"]{background:#edf5f1!important;border:1px solid #d7e5de!important;border-radius:8px!important}
[data-testid="stChatInput"] textarea{background:#edf5f1!important;color:#315b4d!important;font-size:.72rem!important}
[data-testid="stChatInput"] button{background:#0b513d!important;color:white!important}
[data-testid="stChatMessage"]{font-size:.73rem!important;padding:.5rem .65rem!important;border-radius:10px!important}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]){background:#07533d!important;color:white!important;border-color:#07533d!important}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) p{color:white!important}
/* Contrast fixes: Streamlit theme-safe text and controls */
.stButton>button,
.stButton>button p,
.stFormSubmitButton>button,
.stFormSubmitButton>button p{color:#214f42!important;-webkit-text-fill-color:#214f42!important}
.stButton>button[kind="primary"],
.stButton>button[kind="primary"] p,
.stFormSubmitButton>button[kind="primary"],
.stFormSubmitButton>button[kind="primary"] p{background:#07533d!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important;border-color:#07533d!important}
.onko-memory{background:#e5f1eb!important;color:#315d4f!important}
.onko-memory b{background:#07533d!important;color:#ffffff!important;-webkit-text-fill-color:#ffffff!important}
.onko-pill{color:#355d50!important;background:#ffffff!important}
div[data-baseweb="select"]>div,
div[data-baseweb="select"] span{color:#173f34!important;-webkit-text-fill-color:#173f34!important}
.stTextInput input,.stTextArea textarea{color:#173f34!important;-webkit-text-fill-color:#173f34!important}
.stTextInput input::placeholder,.stTextArea textarea::placeholder{color:#789087!important;-webkit-text-fill-color:#789087!important;opacity:1!important}
[data-testid="stChatInput"]{background:#edf5f1!important}
[data-testid="stChatInput"] textarea{color:#173f34!important;-webkit-text-fill-color:#173f34!important}
[data-testid="stChatInput"] textarea::placeholder{color:#789087!important;-webkit-text-fill-color:#789087!important;opacity:1!important}
[data-testid="stChatInput"] button{background:#07533d!important;color:#fff!important}
[data-testid="stChatInput"] button svg{fill:#fff!important;color:#fff!important}
[data-testid="stPills"] button,
[data-testid="stPills"] button p,
[data-testid="stPills"] button span{background:#e3f3ea!important;color:#315f50!important;-webkit-text-fill-color:#315f50!important;border-color:#d1e9dc!important}
[data-testid="stPills"] button[aria-pressed="true"],
[data-testid="stPills"] button[aria-pressed="true"] p,
[data-testid="stPills"] button[aria-pressed="true"] span{background:#afe9cb!important;color:#123f35!important;-webkit-text-fill-color:#123f35!important;border-color:#afe9cb!important}

/* Care-status semantic colors */
div[role="radiogroup"] label:nth-child(1){background:#e5f5ec!important;border-color:#c9e7d7!important}
div[role="radiogroup"] label:nth-child(1) p{color:#176146!important;-webkit-text-fill-color:#176146!important}
div[role="radiogroup"] label:nth-child(2){background:#fff0ef!important;border-color:#f1cbc7!important}
div[role="radiogroup"] label:nth-child(2) p{color:#a63f37!important;-webkit-text-fill-color:#a63f37!important}
div[role="radiogroup"] label:nth-child(3){background:#fff4e4!important;border-color:#efd7b4!important}
div[role="radiogroup"] label:nth-child(3) p{color:#945b16!important;-webkit-text-fill-color:#945b16!important}
div[role="radiogroup"] label:nth-child(1):has(input:checked){background:#bcebd2!important;border-color:#9eddbc!important}
div[role="radiogroup"] label:nth-child(2):has(input:checked){background:#ffd7d2!important;border-color:#efaaa2!important}
div[role="radiogroup"] label:nth-child(3):has(input:checked){background:#ffdba8!important;border-color:#e9bd7d!important}
div[role="radiogroup"] label:nth-child(1):has(input:checked) p{color:#0c543b!important}
div[role="radiogroup"] label:nth-child(2):has(input:checked) p{color:#8d2d27!important}
div[role="radiogroup"] label:nth-child(3):has(input:checked) p{color:#75450f!important}

/* Mood selector should stay neutral/mint instead of inheriting status red/amber */
div[role="radiogroup"]:has(input[aria-label="Mood"]) label{background:#edf5f1!important;border-color:#d8e7df!important}
div[role="radiogroup"]:has(input[aria-label="Mood"]) label p{color:#315d4f!important;-webkit-text-fill-color:#315d4f!important}
div[role="radiogroup"]:has(input[aria-label="Mood"]) label:has(input:checked){background:#afe9cb!important;border-color:#afe9cb!important}

/* Keep forms compact like the reference */
[data-testid="stVerticalBlock"]{gap:.72rem}
.onko-footer{font-size:.6rem!important;margin-top:1.6rem!important}
</style>

"""
