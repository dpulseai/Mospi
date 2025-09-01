# llm_router.py
from __future__ import annotations
from typing import Optional

from config import PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, HF_MODEL, HF_MODELS

# Optional OpenAI (kept import but not required at runtime unless provider=openai)
try:
    from langchain_openai import ChatOpenAI  # noqa: F401
except Exception:
    ChatOpenAI = None  # type: ignore

from transformers import pipeline
try:
    from langchain_community.llms import HuggingFacePipeline
except Exception:
    from langchain.llms import HuggingFacePipeline  # type: ignore


class LLMRouter:
    """Simple provider router. Defaults to Hugging Face if not 'openai'. Supports multiple HF models fallback."""

    def __init__(self):
        self.provider = (PROVIDER or "huggingface").lower()

    def get_chat_model(self):
        if self.provider == "openai":
            if ChatOpenAI is None:
                raise ImportError(
                    "langchain-openai not installed. Run: pip install langchain-openai"
                )
            if not OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in environment")
            # Note: token limits are managed server-side; we keep temperature low for consistency
            return ChatOpenAI(model=OPENAI_MODEL, temperature=0.2, api_key=OPENAI_API_KEY)
        # Hugging Face fallback: try models in order
        last_err: Optional[Exception] = None
        for model_name in HF_MODELS:
            try:
                gen = pipeline("text-generation", model=model_name, max_length=1024)
                return HuggingFacePipeline(pipeline=gen)
            except Exception as e:
                last_err = e
                continue
        # If all fail, raise the last error
        if last_err:
            raise last_err
        # Ultimate fallback: single model
        gen = pipeline("text-generation", model=HF_MODEL, max_length=1024)
        return HuggingFacePipeline(pipeline=gen)

    def get_hf_generator(self):
        """Return raw HF pipeline for direct generation when needed (tries list)."""
        last_err: Optional[Exception] = None
        for model_name in HF_MODELS:
            try:
                return pipeline("text-generation", model=model_name, max_length=1024)
            except Exception as e:
                last_err = e
                continue
        if last_err:
            raise last_err
        return pipeline("text-generation", model=HF_MODEL, max_length=1024)