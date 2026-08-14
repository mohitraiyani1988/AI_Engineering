from dataclasses import dataclass
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_mistralai import ChatMistralAI

from app.config import Settings, get_settings
from app.schemas import ModelOption


Provider = Literal["gemini", "groq", "mistral"]


class ModelNotFoundError(ValueError):
    pass


class ModelNotConfiguredError(ValueError):
    pass


@dataclass(frozen=True)
class ModelDefinition:
    id: str
    provider: Provider
    display_name: str
    model_name: str
    api_key: str

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())

    def as_public_option(self) -> ModelOption:
        return ModelOption(
            id=self.id,
            provider=self.provider,
            display_name=self.display_name,
            model_name=self.model_name,
            configured=self.configured,
        )


def get_model_definitions(settings: Settings | None = None) -> dict[str, ModelDefinition]:
    settings = settings or get_settings()
    definitions = [
        ModelDefinition(
            id="gemini-flash",
            provider="gemini",
            display_name="Gemini Flash",
            model_name=settings.gemini_model,
            api_key=settings.gemini_api_key,
        ),
        ModelDefinition(
            id="groq-llama",
            provider="groq",
            display_name="Groq — Llama",
            model_name=settings.groq_model,
            api_key=settings.groq_api_key,
        ),
        ModelDefinition(
            id="mistral-small",
            provider="mistral",
            display_name="Mistral Small",
            model_name=settings.mistral_model,
            api_key=settings.mistral_api_key,
        ),
    ]
    return {definition.id: definition for definition in definitions}


def get_model_definition(model_id: str) -> ModelDefinition:
    definition = get_model_definitions().get(model_id)
    if definition is None:
        raise ModelNotFoundError(f"Unknown model_id: {model_id}")
    return definition


def create_chat_model(model_id: str) -> tuple[ModelDefinition, BaseChatModel]:
    definition = get_model_definition(model_id)
    if not definition.configured:
        raise ModelNotConfiguredError(
            f"{definition.display_name} is not configured. Add its API key to .env."
        )

    if definition.provider == "gemini":
        model = ChatGoogleGenerativeAI(
            model=definition.model_name,
            google_api_key=definition.api_key,
        )
    elif definition.provider == "groq":
        model = ChatGroq(model=definition.model_name, api_key=definition.api_key)
    else:
        model = ChatMistralAI(model=definition.model_name, api_key=definition.api_key)

    return definition, model
