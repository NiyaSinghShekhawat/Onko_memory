# AGENTS.md — rules for every AI coding agent on this repo

> Claude reads `CLAUDE.md`, ChatGPT/Codex reads `AGENTS.md`. Both files are identical.
> ChatGPT (web): paste this file + `core/contracts.py` at the start of every chat.

## Project
**OnKo Memory** — a cancer-care assistant built on **Hindsight** (memory), **Streamlit** (UI),
**Groq** (LLM) and **SQLite** (app data). The doctor enters the care plan, the patient logs
their day, and a chatbot remembers everything. The doctor makes all clinical decisions.

## Folder ownership — ONLY edit files in your owner's folder
| Owner | Files |
|---|---|
| **Shreyan** | `core/ai/*`, `seed/*`, `README.md` |
| **Samprada** | `core/memory.py`, `core/db.py`, `core/schedule.py`, `core/chat.py`, `core/config.py`, `requirements.txt` |
| **Niya** | `app/*` |
| **Locked (team decision only)** | `core/contracts.py`, `AGENTS.md`, `CLAUDE.md` |

## Hard rules
1. **Never edit `core/contracts.py`.** Never change a dataclass field or a function signature listed in its PUBLIC API.
2. **Only edit files you were asked to edit.** No renaming, refactoring or reformatting other files.
3. **Only call functions that exist** in `contracts.py`'s PUBLIC API. Don't invent helpers in another owner's module.
4. **No new dependencies** without saying so explicitly (Samprada updates `requirements.txt`).
5. Streamlit pages call `core/` functions. They never talk to Hindsight, Groq or SQLite directly.
6. Keep functions small, typed, with a one-line docstring.
7. Never commit `.env`, API keys or `data/*.db`.
8. Never run `git push --force`, `git reset --hard` or delete branches.

## Safety rules (product)
The AI may **organize, summarize and structure** information. It must **never** diagnose,
say a lab value is normal/abnormal, or advise starting/stopping/changing a medicine.
Danger words go straight to the emergency reply in `core/chat.py`.

## How to run
```bash
pip install -r requirements.txt
cp .env.example .env            # fill in keys
python -m scripts.check_setup   # verify Hindsight + Groq
streamlit run app/Home.py
```
