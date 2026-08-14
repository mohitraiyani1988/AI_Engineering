from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)

    @field_validator("content")
    @classmethod
    def clean_content(cls, value: str) -> str:
        return value.strip()


class ChatStreamRequest(BaseModel):
    model_id: str
    message: str = Field(min_length=1, max_length=20_000)
    history: list[ConversationMessage] = Field(default_factory=list, max_length=100)

    @field_validator("model_id", "message")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        return value.strip()


class TemplateStreamRequest(BaseModel):
    model_id: str
    inputs: dict[str, Any]

    @field_validator("model_id")
    @classmethod
    def clean_model_id(cls, value: str) -> str:
        return value.strip()


class ModelOption(BaseModel):
    id: str
    provider: Literal["gemini", "groq", "mistral"]
    display_name: str
    model_name: str
    configured: bool


class TemplateField(BaseModel):
    name: str
    label: str
    type: Literal["text", "select", "number"]
    required: bool = True
    options: list[str] = Field(default_factory=list)
    default: str | int | None = None


class TemplateOption(BaseModel):
    id: str
    name: str
    description: str
    fields: list[TemplateField]
