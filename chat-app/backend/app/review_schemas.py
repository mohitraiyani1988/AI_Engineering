from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ReviewAnalysis(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    rating: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=500)
    pros: list[str]
    cons: list[str]
    recommendation: bool


class ReviewAnalysisRequest(BaseModel):
    review: str = Field(min_length=5, max_length=20_000)
    model_ids: list[str] = Field(
        default_factory=lambda: [
            "gemini-flash",
            "groq-llama",
            "mistral-small",
        ],
        min_length=1,
        max_length=3,
    )
    strategy: Literal["native", "parser"] = "native"

    @field_validator("review")
    @classmethod
    def clean_review(cls, value: str) -> str:
        return value.strip()

    @field_validator("model_ids")
    @classmethod
    def unique_model_ids(cls, values: list[str]) -> list[str]:
        cleaned = [value.strip() for value in values]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("model_ids must not contain duplicates")
        return cleaned
