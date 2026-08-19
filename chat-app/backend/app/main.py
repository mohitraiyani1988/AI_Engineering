import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routes.chat import router as chat_router
from app.routes.catalog import router as catalog_router
from app.routes.reviews import router as reviews_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

app = FastAPI(
    title="Multi-Model LangChain Chat Backend",
    description="FastAPI backend for general and template-based streaming chat.",
    version="2.0.0",
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(catalog_router)
app.include_router(reviews_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
