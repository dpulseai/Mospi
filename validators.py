# validators.py
from __future__ import annotations
from typing import Dict, Any, List

CHOICE_TYPES = {"single-choice", "multiple-choice"}
VALID_TYPES = {"open-ended", "single-choice", "multiple-choice", "rating"}


def _coerce_area(area: str) -> str:
    a = (area or "").strip().lower()
    if a.startswith("rur"):
        return "Rural"
    if a.startswith("urb"):
        return "Urban"
    return area or "Rural"


def _ensure_id(i: int) -> str:
    return f"q{i}"


def validate_and_fix_survey(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and minimally fix survey JSON.
    - Ensures required top-level fields
    - Normalizes area_type
    - Validates question structure and types
    - Ensures options only for choice types and 3-6 options if present
    """
    fixed = dict(data)
    fixed.setdefault("title", fixed.get("domain", "Survey"))
    fixed.setdefault("domain", "General")
    fixed.setdefault("region", "Unknown")
    fixed["area_type"] = _coerce_area(fixed.get("area_type", "Rural"))
    fixed.setdefault("language", "English")

    questions: List[Dict[str, Any]] = fixed.get("questions") or []
    new_qs: List[Dict[str, Any]] = []
    for i, q in enumerate(questions, start=1):
        q = dict(q)
        q.setdefault("id", _ensure_id(i))
        q.setdefault("text", "")
        qtype = q.get("type", "open-ended")
        if qtype not in VALID_TYPES:
            qtype = "open-ended"
        q["type"] = qtype
        if qtype in CHOICE_TYPES:
            opts = q.get("options") or []
            # enforce 3-6 options if available
            if isinstance(opts, list):
                if len(opts) < 3:
                    # pad with generic
                    base = ["Yes", "No", "Not sure"]
                    for o in base:
                        if len(opts) >= 3:
                            break
                        if o not in opts:
                            opts.append(o)
                if len(opts) > 6:
                    opts = opts[:6]
            else:
                opts = ["Yes", "No", "Not sure"]
            q["options"] = opts
        else:
            q["options"] = None
        new_qs.append(q)
    fixed["questions"] = new_qs
    return fixed