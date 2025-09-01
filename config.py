import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API keys (OpenAI optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")  # optional
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "survey")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")  # optional


PROVIDER = os.getenv("LLM_PROVIDER", "huggingface")  # "openai" or "huggingface"

# OpenAI config (used only if PROVIDER=openai)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
# User requested ~5000 requested tokens; this is a target upper bound. Actual API limits may be lower.
OPENAI_MAX_OUTPUT_TOKENS = int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "5000"))


HF_MODEL = os.getenv("HF_MODEL", "microsoft/DialoGPT-medium")
HF_MODELS = [m.strip() for m in os.getenv("HF_MODELS", HF_MODEL).split(",") if m.strip()]
