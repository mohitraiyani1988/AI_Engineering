import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field


BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPOSITORY_ROOT = BACKEND_ROOT.parent.parent
ROOT_ENV_PATH = REPOSITORY_ROOT / ".env"
BACKEND_ENV_PATH = BACKEND_ROOT / ".env"

# The repository-level file is primary. A backend-local file is also supported
# when this application is later deployed independently.
load_dotenv(ROOT_ENV_PATH, override=False)
load_dotenv(BACKEND_ENV_PATH, override=False)


class Settings(BaseModel):
    gemini_api_key: str = ""
    groq_api_key: str = ""
    mistral_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    groq_model: str = "llama-3.3-70b-versatile"
    mistral_model: str = "mistral-small-latest"
    cors_allowed_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:4200",
            "http://127.0.0.1:4200",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    cors_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:4200,http://127.0.0.1:4200",
        ).split(",")
        if origin.strip()
    ]
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
        mistral_api_key=os.getenv("MISTRAL_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
        groq_model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        mistral_model=os.getenv("MISTRAL_MODEL", "mistral-small-latest"),
        cors_allowed_origins=cors_origins,
    )
