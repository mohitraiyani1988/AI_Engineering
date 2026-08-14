import os
from pathlib import Path
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


class Settings(BaseModel):
    google_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"
    env_path: str = str(ENV_PATH)

    @property
    def masked_google_api_key(self) -> str:
        if not self.google_api_key:
            return "<missing>"

        return f"{self.google_api_key[:6]}...{self.google_api_key[-4:]}"


@lru_cache
def get_settings() -> Settings:
    return Settings(
        google_api_key=os.getenv("GOOGLE_API_KEY", ""),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    )
