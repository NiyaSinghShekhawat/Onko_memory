"""
PDF report → text → structured values. Owner: Shreyan.

Only EXTRACTS what is written. Never says if a value is normal/abnormal.
Scanned (image-only) PDFs return empty text for now — add OCR later if time allows.
"""

from __future__ import annotations

import io

from core import config
from core.ai.llm import chat_json
from core.contracts import ExtractedReport, ReportValue

SYSTEM_PROMPT = """You extract values from a medical report's text.
Return JSON: {"report_name": string, "report_date": "YYYY-MM-DD" or "",
"values": [{"name": string, "value": string, "unit": string}]}
Rules: copy values exactly as written. Do NOT add reference ranges, flags,
interpretations, or any value that is not in the text."""


def read_pdf_text(file_bytes: bytes) -> str:
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(file_bytes))
    return "\n".join((page.extract_text() or "") for page in reader.pages).strip()


def extract_report(text: str) -> ExtractedReport:
    if not text:  # scanned PDF with no text layer
        return ExtractedReport("Unreadable report", "", [], "")
    if config.USE_STUBS:
        return ExtractedReport("CBC (stub)", "", [ReportValue("Hb", "9.2", "g/dL")], text)
    data = chat_json(SYSTEM_PROMPT, text[:12000])
    values = [
        ReportValue(str(v.get("name", "")), str(v.get("value", "")), str(v.get("unit", "") or ""))
        for v in data.get("values", []) if v.get("name")
    ]
    return ExtractedReport(str(data.get("report_name", "Report")), str(data.get("report_date", "") or ""), values, text)
