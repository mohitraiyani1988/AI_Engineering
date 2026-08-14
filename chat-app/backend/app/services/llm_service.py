from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.runnables import Runnable

from app.models import ModelDefinition


def content_to_text(content: str | list[str | dict[str, Any]]) -> str:
    if isinstance(content, str):
        return content
    return "".join(
        item if isinstance(item, str) else str(item.get("text", ""))
        for item in content
    )


def find_metadata_value(metadata: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in metadata:
            return metadata[name]
    for value in metadata.values():
        if isinstance(value, dict):
            found = find_metadata_value(value, *names)
            if found is not None:
                return found
    return None


def normalize_details(
    definition: ModelDefinition,
    response: AIMessageChunk,
    *,
    latency_ms: int,
    time_to_first_token_ms: int | None,
    chunk_count: int,
) -> dict[str, Any]:
    usage = response.usage_metadata or {}
    metadata = response.response_metadata or {}
    return {
        "provider": definition.provider,
        "model_id": definition.id,
        "model_name": definition.model_name,
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "reasoning_tokens": find_metadata_value(
            {"usage": usage, "response": metadata},
            "reasoning_tokens",
            "reasoning_token_count",
            "thoughts_token_count",
        ),
        "finish_reason": find_metadata_value(
            metadata,
            "finish_reason",
            "stop_reason",
        ),
        "latency_ms": latency_ms,
        "time_to_first_token_ms": time_to_first_token_ms,
        "chunk_count": chunk_count,
        "raw_usage_metadata": usage,
        "raw_response_metadata": metadata,
    }


async def stream_runnable(
    runnable: Runnable[Any, BaseMessage],
    runnable_input: Any,
) -> AsyncGenerator[tuple[str, AIMessageChunk], None]:
    """Yield text chunks together with the accumulated LangChain response."""
    accumulated = AIMessageChunk(content="")
    async for chunk in runnable.astream(runnable_input):
        accumulated += chunk
        yield content_to_text(chunk.content), accumulated
