import os
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI


Provider = Literal["gemini", "groq", "mistral"]


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise ValueError(f"{name} is missing. Add it to the repository .env file.")
    return value


def create_chat_model(provider: Provider) -> BaseChatModel:
    """Create a LangChain chat model from one safe provider identifier."""
    if provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            google_api_key=_required_env("GEMINI_API_KEY"),
        )

    if provider == "groq":
        return ChatGroq(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            api_key=_required_env("GROQ_API_KEY"),
        )

    if provider == "mistral":
        return ChatMistralAI(
            model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
            api_key=_required_env("MISTRAL_API_KEY"),
        )

    raise ValueError(f"Unsupported provider: {provider}")
