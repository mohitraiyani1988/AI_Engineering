import time
from typing import Any, Literal

from langchain_core.messages import AIMessage
from langchain_core.output_parsers import PydanticOutputParser

from app.models import create_chat_model
from app.review_prompts import REVIEW_ANALYSIS_PROMPT
from app.review_schemas import ReviewAnalysis
from app.services.llm_service import normalize_details


Strategy = Literal["native", "parser"]


class ReviewParsingError(ValueError):
    pass


def _validated_analysis(value: Any) -> ReviewAnalysis:
    if isinstance(value, ReviewAnalysis):
        return value
    return ReviewAnalysis.model_validate(value)


async def analyze_review(
    model_id: str,
    review: str,
    strategy: Strategy,
) -> dict[str, Any]:
    """Run one provider pipeline and return a normalized comparison result."""
    definition, model = create_chat_model(model_id)
    started = time.perf_counter()

    if strategy == "native":
        native_prompt = REVIEW_ANALYSIS_PROMPT.partial(
            format_instructions="Follow the structured schema supplied by the model API."
        )
        chain = native_prompt | model.with_structured_output(
            ReviewAnalysis,
            include_raw=True,
        )
        result = await chain.ainvoke({"review": review})
        raw = result.get("raw")
        parsing_error = result.get("parsing_error")
        if parsing_error is not None:
            raise ReviewParsingError(str(parsing_error))
        analysis = _validated_analysis(result.get("parsed"))
    else:
        parser = PydanticOutputParser(pydantic_object=ReviewAnalysis)
        parser_prompt = REVIEW_ANALYSIS_PROMPT.partial(
            format_instructions=parser.get_format_instructions()
        )
        # The explicit parser strategy intentionally exposes each stage:
        # prompt -> model text -> PydanticOutputParser -> ReviewAnalysis.
        prompt_value = await parser_prompt.ainvoke({"review": review})
        raw = await model.ainvoke(prompt_value)
        analysis = await parser.ainvoke(raw)

    if not isinstance(raw, AIMessage):
        raise ReviewParsingError("The provider did not return an AIMessage.")

    latency_ms = int((time.perf_counter() - started) * 1000)
    details = normalize_details(
        definition,
        raw,
        latency_ms=latency_ms,
        time_to_first_token_ms=None,
        chunk_count=1,
    )
    return {
        "model_id": definition.id,
        "provider": definition.provider,
        "model_name": definition.model_name,
        "strategy": strategy,
        "analysis": analysis.model_dump(),
        "details": details,
    }
