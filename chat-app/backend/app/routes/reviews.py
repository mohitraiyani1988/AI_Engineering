import asyncio
import logging
from collections.abc import AsyncGenerator
from uuid import uuid4

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.review_schemas import ReviewAnalysisRequest
from app.routes.chat import sse_event
from app.services.review_analysis_service import Strategy, analyze_review


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/reviews", tags=["review analysis"])


async def _safe_analysis(model_id: str, review: str, strategy: Strategy) -> dict:
    try:
        result = await analyze_review(model_id, review, strategy)
        return {"success": True, "model_id": model_id, "result": result}
    except Exception as error:
        logger.exception("Review analysis failed for model_id=%s", model_id)
        return {
            "success": False,
            "model_id": model_id,
            "error_type": type(error).__name__,
            "message": str(error),
        }


@router.post("/analyze/stream")
async def stream_review_analysis(
    payload: ReviewAnalysisRequest,
    request: Request,
) -> StreamingResponse:
    analysis_id = str(uuid4())

    async def event_generator() -> AsyncGenerator[str, None]:
        tasks = [
            asyncio.create_task(
                _safe_analysis(model_id, payload.review, payload.strategy)
            )
            for model_id in payload.model_ids
        ]
        successful = 0
        failed = 0

        yield sse_event(
            "start",
            {
                "analysis_id": analysis_id,
                "model_ids": payload.model_ids,
                "strategy": payload.strategy,
            },
        )

        try:
            for completed in asyncio.as_completed(tasks):
                if await request.is_disconnected():
                    for task in tasks:
                        task.cancel()
                    return

                outcome = await completed
                if outcome["success"]:
                    successful += 1
                    yield sse_event(
                        "model_result",
                        {
                            "analysis_id": analysis_id,
                            **outcome["result"],
                        },
                    )
                else:
                    failed += 1
                    yield sse_event(
                        "model_error",
                        {
                            "analysis_id": analysis_id,
                            "model_id": outcome["model_id"],
                            "error_type": outcome["error_type"],
                            "message": outcome["message"],
                        },
                    )
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()

        yield sse_event(
            "done",
            {
                "analysis_id": analysis_id,
                "successful": successful,
                "failed": failed,
            },
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
