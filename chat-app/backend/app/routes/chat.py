import json
import logging
import time
from collections.abc import AsyncGenerator
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.models import (
    ModelNotConfiguredError,
    ModelNotFoundError,
    create_chat_model,
)
from app.schemas import ChatStreamRequest, TemplateStreamRequest
from app.services.llm_service import normalize_details, stream_runnable
from app.templates import TemplateInputError, TemplateNotFoundError, get_template


logger = logging.getLogger(__name__)
router = APIRouter(tags=["chat"])

GENERAL_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful AI assistant. Give clear and accurate answers."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{message}"),
    ]
)


def sse_event(event: str, data: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False, default=str)}\n\n"


def http_error_from_model(error: ValueError) -> HTTPException:
    if isinstance(error, ModelNotFoundError):
        return HTTPException(status_code=404, detail=str(error))
    return HTTPException(status_code=503, detail=str(error))


def streaming_response(
    *,
    request: Request,
    definition: Any,
    runnable: Any,
    runnable_input: Any,
    mode: str,
) -> StreamingResponse:
    message_id = str(uuid4())

    async def event_generator() -> AsyncGenerator[str, None]:
        started = time.perf_counter()
        first_token_ms: int | None = None
        chunk_count = 0
        accumulated = None

        yield sse_event(
            "start",
            {
                "message_id": message_id,
                "mode": mode,
                "provider": definition.provider,
                "model_id": definition.id,
                "model_name": definition.model_name,
            },
        )

        try:
            async for text, accumulated in stream_runnable(runnable, runnable_input):
                if await request.is_disconnected():
                    logger.info("Client disconnected from message %s", message_id)
                    return
                chunk_count += 1
                if text:
                    if first_token_ms is None:
                        first_token_ms = int((time.perf_counter() - started) * 1000)
                    yield sse_event("token", {"message_id": message_id, "text": text})

            latency_ms = int((time.perf_counter() - started) * 1000)
            if accumulated is None:
                raise RuntimeError("The model stream completed without a response.")
            yield sse_event(
                "done",
                {
                    "message_id": message_id,
                    "details": normalize_details(
                        definition,
                        accumulated,
                        latency_ms=latency_ms,
                        time_to_first_token_ms=first_token_ms,
                        chunk_count=chunk_count,
                    ),
                },
            )
        except Exception:
            latency_ms = int((time.perf_counter() - started) * 1000)
            logger.exception("Streaming failed for message %s", message_id)
            yield sse_event(
                "error",
                {
                    "message_id": message_id,
                    "code": "provider_error",
                    "message": "The selected model could not complete this request.",
                    "latency_ms": latency_ms,
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


@router.post("/chat/stream")
async def stream_chat(payload: ChatStreamRequest, request: Request) -> StreamingResponse:
    try:
        definition, model = create_chat_model(payload.model_id)
    except (ModelNotFoundError, ModelNotConfiguredError) as error:
        raise http_error_from_model(error) from error

    history = [
        HumanMessage(content=item.content)
        if item.role == "user"
        else AIMessage(content=item.content)
        for item in payload.history
    ]
    chain = GENERAL_CHAT_PROMPT | model
    return streaming_response(
        request=request,
        definition=definition,
        runnable=chain,
        runnable_input={"history": history, "message": payload.message},
        mode="general",
    )


@router.post("/templates/{template_id}/stream")
async def stream_template_chat(
    template_id: str,
    payload: TemplateStreamRequest,
    request: Request,
) -> StreamingResponse:
    try:
        template = get_template(template_id)
        inputs = template.validate_inputs(payload.inputs)
    except TemplateNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except TemplateInputError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    try:
        definition, model = create_chat_model(payload.model_id)
    except (ModelNotFoundError, ModelNotConfiguredError) as error:
        raise http_error_from_model(error) from error

    chain = template.prompt | model
    return streaming_response(
        request=request,
        definition=definition,
        runnable=chain,
        runnable_input=inputs,
        mode="template",
    )
