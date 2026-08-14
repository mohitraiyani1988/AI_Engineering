import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, AIMessageChunk, HumanMessage, SystemMessage


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from langchain_lab.models import Provider, create_chat_model  # noqa: E402


Method = Literal["invoke", "ainvoke", "stream", "astream"]

load_dotenv(REPOSITORY_ROOT / ".env")

MESSAGES = [
    SystemMessage(content="You are a concise AI engineering tutor."),
    HumanMessage(content="Explain the difference between an LLM and an AI application."),
]


def printable_content(content: str | list[str | dict[str, Any]]) -> str:
    if isinstance(content, str):
        return content
    return "".join(
        item if isinstance(item, str) else str(item.get("text", ""))
        for item in content
    )


def find_metadata_value(metadata: dict[str, Any], *names: str) -> Any:
    """Find a provider-specific value in a small nested metadata dictionary."""
    for name in names:
        if name in metadata:
            return metadata[name]

    for value in metadata.values():
        if isinstance(value, dict):
            found = find_metadata_value(value, *names)
            if found is not None:
                return found

    return None


def print_details(
    *,
    provider: Provider,
    method: Method,
    model_name: str,
    response: AIMessage | AIMessageChunk,
    response_text: str,
    elapsed_seconds: float,
    time_to_first_token_seconds: float | None,
    chunk_count: int | None,
) -> None:
    usage = response.usage_metadata or {}
    metadata = response.response_metadata or {}

    input_tokens = usage.get("input_tokens")
    output_tokens = usage.get("output_tokens")
    total_tokens = usage.get("total_tokens")
    reasoning_tokens = find_metadata_value(
        {"usage": usage, "response": metadata},
        "reasoning_tokens",
        "reasoning_token_count",
        "thoughts_token_count",
    )
    finish_reason = find_metadata_value(
        metadata,
        "finish_reason",
        "stop_reason",
    )

    print("\n\n" + "=" * 70)
    print("LANGCHAIN INVOCATION REPORT")
    print("=" * 70)
    print(f"Provider:            {provider}")
    print(f"Model:               {model_name}")
    print(f"Method:              {method}")
    print(f"Input tokens:        {input_tokens if input_tokens is not None else 'not provided'}")
    print(f"Output tokens:       {output_tokens if output_tokens is not None else 'not provided'}")
    print(f"Total tokens:        {total_tokens if total_tokens is not None else 'not provided'}")
    print(f"Reasoning tokens:    {reasoning_tokens if reasoning_tokens is not None else 'not provided'}")
    print(f"Finish reason:       {finish_reason if finish_reason is not None else 'not provided'}")
    print(f"Total latency:       {elapsed_seconds * 1000:.0f} ms")
    if time_to_first_token_seconds is None:
        print("Time to first token: not applicable (non-streaming method)")
    else:
        print(f"Time to first token: {time_to_first_token_seconds * 1000:.0f} ms")
    print(f"Stream chunks:       {chunk_count if chunk_count is not None else 'not applicable'}")
    print("Error:               none")
    print("\nResponse:")
    print(response_text)
    print("\nRaw usage metadata:")
    print(json.dumps(usage, indent=2, default=str))
    print("\nRaw response metadata:")
    print(json.dumps(metadata, indent=2, default=str))


async def run(provider: Provider, method: Method) -> None:
    model = create_chat_model(provider)
    model_name = str(getattr(model, "model", getattr(model, "model_name", "unknown")))
    started = time.perf_counter()
    time_to_first_token: float | None = None
    chunk_count: int | None = None

    if method == "invoke":
        response = model.invoke(MESSAGES)
        response_text = printable_content(response.content)
    elif method == "ainvoke":
        response = await model.ainvoke(MESSAGES)
        response_text = printable_content(response.content)
    elif method == "stream":
        response = AIMessageChunk(content="")
        chunks: list[str] = []
        chunk_count = 0
        print("Streaming response:\n")
        for chunk in model.stream(MESSAGES):
            text = printable_content(chunk.content)
            if text and time_to_first_token is None:
                time_to_first_token = time.perf_counter() - started
            response += chunk
            chunks.append(text)
            chunk_count += 1
            print(text, end="", flush=True)
        response_text = "".join(chunks)
    else:
        response = AIMessageChunk(content="")
        chunks = []
        chunk_count = 0
        print("Streaming response:\n")
        async for chunk in model.astream(MESSAGES):
            text = printable_content(chunk.content)
            if text and time_to_first_token is None:
                time_to_first_token = time.perf_counter() - started
            response += chunk
            chunks.append(text)
            chunk_count += 1
            print(text, end="", flush=True)
        response_text = "".join(chunks)

    print_details(
        provider=provider,
        method=method,
        model_name=model_name,
        response=response,
        response_text=response_text,
        elapsed_seconds=time.perf_counter() - started,
        time_to_first_token_seconds=time_to_first_token,
        chunk_count=chunk_count,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare LangChain invocation methods.")
    parser.add_argument("--provider", choices=["gemini", "groq", "mistral"], required=True)
    parser.add_argument("--method", choices=["invoke", "ainvoke", "stream", "astream"], required=True)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    try:
        asyncio.run(run(arguments.provider, arguments.method))
    except Exception as error:
        print("\n" + "=" * 70, file=sys.stderr)
        print("LANGCHAIN INVOCATION ERROR", file=sys.stderr)
        print("=" * 70, file=sys.stderr)
        print(f"Provider:   {arguments.provider}", file=sys.stderr)
        print(f"Method:     {arguments.method}", file=sys.stderr)
        print(f"Error type: {type(error).__name__}", file=sys.stderr)
        print(f"Message:    {error}", file=sys.stderr)
        raise SystemExit(1) from error
