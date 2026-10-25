import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama


def create_llm():
    provider = (
        os.getenv(
            "LLM_PROVIDER",
            "gemini",
        )
        .strip()
        .lower()
    )

    if provider == "gemini":
        api_key = os.getenv("GOOGLE_API_KEY")

        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY is missing")

        model_name = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        )

        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0,
        )

    if provider == "ollama":
        model_name = os.getenv(
            "OLLAMA_MODEL",
            "qwen2.5-coder:7b",
        )

        base_url = os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434",
        )

        return ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0,
            num_ctx=8192,
        )

    raise ValueError(f"Unsupported LLM provider: {provider}")
