import logging

from fastapi import FastAPI

from app.config import get_settings
from app.routes.chat import router as chat_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(
    title="Gemini SSE Chat Backend",
    description="FastAPI backend that streams Google Gemini responses with Server-Sent Events.",
    version="1.0.0",
)

app.include_router(chat_router)

settings = get_settings()
logging.getLogger(__name__).info(
    "Loaded settings from %s with GOOGLE_API_KEY=%s and GEMINI_MODEL=%s",
    settings.env_path,
    settings.masked_google_api_key,
    settings.gemini_model,
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
