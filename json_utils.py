# json_utils.py
from __future__ import annotations
import json
import re
from typing import Any, Dict


def extract_json(text: str) -> Dict[str, Any]:
    """Extract first JSON object from text. Raises ValueError if none found or invalid.
    Handles cases where model adds prose around the JSON.
    """
    # Find the first balanced {...}
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        # Try code block style ```json ... ```
        code_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", text, re.IGNORECASE)
        if code_match:
            return json.loads(code_match.group(1))
        raise ValueError("No JSON object found in model output")
    candidate = text[start : end + 1]
    # Remove trailing commas which some models emit
    candidate = re.sub(r",(\s*[}\]])", r"\1", candidate)
    return json.loads(candidate)


def json_to_text(payload: Dict[str, Any]) -> str:
    """Convert survey JSON to a readable plain text representation for exports."""
    lines = []
    title = payload.get("title", "Survey")
    domain = payload.get("domain", "")
    region = payload.get("region", "")
    area_type = payload.get("area_type", "")
    header = title
    meta = ", ".join(x for x in [domain, region, area_type] if x)
    if meta:
        header += f" ({meta})"
    lines.append(header)
    lines.append("")
    for i, q in enumerate(payload.get("questions", []), start=1):
        qtext = q.get("text", "").strip()
        qtype = q.get("type", "").strip()
        lines.append(f"Q{i}. {qtext} [{qtype}]")
        opts = q.get("options")
        if isinstance(opts, list) and opts:
            for idx, opt in enumerate(opts, start=1):
                lines.append(f"  {idx}. {opt}")
        lines.append("")
    return "\n".join(lines).strip()