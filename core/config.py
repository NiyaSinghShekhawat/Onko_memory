"""Loads settings from .env. Owner: Samprada. Everyone reads, only the owner edits."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# Hindsight
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "").strip()
HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip() or None
# Each developer uses their own prefix (dev-shreyan, dev-samprada, dev-niya).
# Only the final demo uses "demo".
HINDSIGHT_BANK_PREFIX = os.getenv("HINDSIGHT_BANK_PREFIX", "dev-local").strip()

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()

# App
DB_PATH = Path(os.getenv("ONKO_DB_PATH", str(ROOT / "data" / "onko.db")))
# When 1, AI functions return sample data instead of calling Groq (for UI work).
USE_STUBS = os.getenv("ONKO_STUBS", "0").strip() == "1"
