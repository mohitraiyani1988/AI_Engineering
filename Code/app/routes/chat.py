import json
import logging
import time
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.schemas import ChatStreamRequest
from app.services.llm_service import GeminiLLMService


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


def _sse_event(event: str, data: dict[str, object]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@router.post("/stream")
async def stream_chat(payload: ChatStreamRequest, request: Request) -> StreamingResponse:
    service = GeminiLLMService()

    async def event_generator() -> AsyncGenerator[str, None]:
        start_time = time.perf_counter()
        logger.info("Chat stream request started")

        try:
            yield _sse_event("start", {"message": "stream_started"})

            async for token in service.stream_response(payload.question):
                if await request.is_disconnected():
                    latency_ms = int((time.perf_counter() - start_time) * 1000)
                    logger.info("Client disconnected from chat stream after %sms", latency_ms)
                    return

                yield _sse_event("token", {"text": token})

            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info("Chat stream request completed in %sms", latency_ms)
            yield _sse_event(
                "done",
                {"message": "stream_completed", "latency_ms": latency_ms},
            )
        except Exception:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            logger.exception("Chat stream request failed after %sms", latency_ms)
            yield _sse_event(
                "error",
                {"message": "Sorry, the assistant could not complete this request."},
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
