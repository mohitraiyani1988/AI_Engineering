from collections.abc import AsyncGenerator
import json
import logging
from typing import Any

import httpx
from langchain_core.prompts import ChatPromptTemplate

from app.config import get_settings


logger = logging.getLogger(__name__)


def extract_text_from_interaction_event(event: dict[str, Any]) -> str:
    if event.get("event_type") == "step.delta":
        delta = event.get("delta", {})
        if isinstance(delta, dict) and delta.get("type") == "text":
            return str(delta.get("text", ""))

    output_text = event.get("output_text")
    if isinstance(output_text, str):
        return output_text

    return ""


def extract_sse_data(line: str) -> str:
    if not line.startswith("data:"):
        return ""

    return line.removeprefix("data:").strip()


class GeminiLLMService:
    _interactions_url = "https://generativelanguage.googleapis.com/v1beta/interactions"

    def __init__(self) -> None:
        settings = get_settings()
        self._model = settings.gemini_model
        self._api_key = settings.google_api_key
        self._prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "You are a helpful technical assistant. "
                        "Explain concepts clearly for beginners."
                    ),
                ),
                ("human", "{question}"),
            ]
        )

    async def stream_response(self, question: str) -> AsyncGenerator[str, None]:
        messages = self._prompt.format_messages(question=question)
        system_message = str(messages[0].content)
        user_message = str(messages[1].content)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                self._interactions_url,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self._api_key,
                },
                json={
                    "model": self._model,
                    "input": user_message,
                    "system_instruction": system_message,
                    "stream": True,
                },
            ) as response:
                if response.is_error:
                    body = await response.aread()
                    logger.error(
                        "Gemini Interactions API failed with status=%s body=%s",
                        response.status_code,
                        body.decode("utf-8", errors="replace"),
                    )

                response.raise_for_status()

                async for line in response.aiter_lines():
                    data = extract_sse_data(line)
                    if not data or data == "[DONE]":
                        continue

                    event = json.loads(data)
                    text = extract_text_from_interaction_event(event)
                    if text:
                        yield text
