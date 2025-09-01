# tools_agentic.py
from typing import Callable, Dict, Any
import json
import os
from exports import export_to_json, export_to_csv, export_to_html, export_to_pdf
from utils import ensure_directory_exists
from validators import validate_and_fix_survey

# Tool: save JSON payload to file

def save_json_tool(payload: str) -> str:
    """Save JSON string to ./outputs/surveys/<title|timestamp>.json. Returns path or error."""
    try:
        data = json.loads(payload)
        # validate and minimally fix
        data = validate_and_fix_survey(data)
        title = data.get("title", "survey").strip() or "survey"
        safe_title = "".join(c for c in title if c.isalnum() or c in ("-", "_", " ")).strip().replace(" ", "_")
        out_dir = os.path.join("outputs", "surveys")
        ensure_directory_exists(out_dir)
        path = os.path.join(out_dir, f"{safe_title}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return path
    except Exception as e:
        return f"Error saving JSON: {e}"


def validate_json_tool(payload: str) -> str:
    """Validate and normalize survey JSON; returns the normalized JSON string."""
    try:
        data = json.loads(payload)
        fixed = validate_and_fix_survey(data)
        return json.dumps(fixed, ensure_ascii=False)
    except Exception as e:
        return f"Error validating JSON: {e}"


# Export passthroughs (reuse existing)
export_to_json_tool: Callable[[str], str] = export_to_json
export_to_csv_tool: Callable[[str], str] = export_to_csv
export_to_html_tool: Callable[[str], str] = export_to_html
export_to_pdf_tool: Callable[[str], str] = export_to_pdf


# Tool registry helper

def registry() -> Dict[str, Dict[str, Any]]:
    return {
        "Validate JSON": {
            "func": validate_json_tool,
            "desc": "Validate and normalize survey JSON; returns normalized JSON string",
        },
        "Save JSON": {
            "func": save_json_tool,
            "desc": "Save a survey JSON string to outputs/surveys/<title>.json and return the path.",
        },
        "Export to JSON": {
            "func": export_to_json_tool,
            "desc": "Wrap plain text survey into JSON string with key 'survey'.",
        },
        "Export to CSV": {
            "func": export_to_csv_tool,
            "desc": "Export a plain text survey (newline separated) to CSV file (question column).",
        },
        "Export to HTML": {
            "func": export_to_html_tool,
            "desc": "Export a plain text survey to a basic HTML page.",
        },
        "Export to PDF": {
            "func": export_to_pdf_tool,
            "desc": "Export a plain text survey to a PDF via xhtml2pdf.",
        },
    }