from pydantic import BaseModel, Field, field_validator


class ChatStreamRequest(BaseModel):
    question: str = Field(..., description="User question to send to Gemini.")

    @field_validator("question")
    @classmethod
    def question_must_not_be_empty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question must not be empty.")
        return cleaned
