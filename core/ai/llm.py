"""Small Groq helper shared by the AI modules. Owner: Shreyan."""

from __future__ import annotations

import json
import re

from core import config

try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

_client = None


def _get_client():
    global _client
    if _client is None:
        if Groq is None:
            raise RuntimeError("The 'groq' package is not installed. Run: pip install -r requirements.txt")
        if not config.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is missing in .env")
        _client = Groq(api_key=config.GROQ_API_KEY)
    return _client


def chat_json(system: str, user: str) -> dict:
    """Ask the model for a JSON object and parse it (tolerates code fences)."""
    resp = _get_client().chat.completions.create(
        model=config.GROQ_MODEL,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    raw = resp.choices[0].message.content or "{}"
    raw = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)
