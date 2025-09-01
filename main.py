# main.py

from json import dumps
from json_utils import json_to_text
from survey_generator import generate_survey_json
from tools_agentic import save_json_tool

# Entry point for generating and saving surveys as JSON
# We target Agriculture, Education, Healthcare across regions and area types.

def main():
    domains = ["Agriculture", "Education", "Healthcare"]
    regions = ["Bihar", "Karnataka", "Delhi"]  # example regions; extend as needed
    area_types = ["Rural", "Urban"]

    for domain in domains:
        for region in regions:
            for area in area_types:
                print(f"\nGenerating {domain} survey for {region} ({area})...")
                survey = generate_survey_json(domain, region, area)
                # Save JSON to outputs/surveys/<title>.json
                saved_path = save_json_tool(dumps(survey, ensure_ascii=False))
                print(f"Saved: {saved_path}")
                # Optionally convert to readable text for console
                print("Preview:\n" + json_to_text(survey)[:600] + ("..." if len(json_to_text(survey)) > 600 else ""))


if __name__ == "__main__":
    main()