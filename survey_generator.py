from typing import Dict, Any
from llm_router import LLMRouter
from prompts import build_survey_json_prompt
from json_utils import extract_json


def generate_survey_json(domain: str, region: str, area_type: str, language: str = "English") -> Dict[str, Any]:
    """Generate a structured survey JSON using the selected provider (HF by default).

    Returns a Python dict matching the target schema.
    """
    router = LLMRouter()
    # Prefer a chat-style interface if available; for HF text-generation, we still send a single prompt.
    llm = router.get_chat_model()

    prompt = build_survey_json_prompt(domain, region, area_type, language)

    # Call the model; ChatOpenAI responds with .invoke(), HF LLMs use .invoke() as well in LangChain interface
    try:
        output = llm.invoke(prompt)  # LangChain LLMs expose .invoke for both providers
    except AttributeError:
        # Fallback: some versions use .predict
        output = llm.predict(prompt)

    text = output.content if hasattr(output, "content") else str(output)

    data = extract_json(text)
    # Minimal normalization
    data.setdefault("domain", domain)
    data.setdefault("region", region)
    data.setdefault("area_type", area_type)
    data.setdefault("language", language)
    return data


if __name__ == "__main__":
    sample = generate_survey_json("Agriculture", "Bihar", "Rural")
    import json
    print(json.dumps(sample, ensure_ascii=False, indent=2))