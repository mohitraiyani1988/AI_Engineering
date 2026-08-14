from dataclasses import dataclass
from typing import Any

from langchain_core.prompts import ChatPromptTemplate

from app.schemas import TemplateField, TemplateOption


class TemplateNotFoundError(ValueError):
    pass


class TemplateInputError(ValueError):
    pass


@dataclass(frozen=True)
class PromptTemplateDefinition:
    id: str
    name: str
    description: str
    fields: tuple[TemplateField, ...]
    prompt: ChatPromptTemplate

    def as_public_option(self) -> TemplateOption:
        return TemplateOption(
            id=self.id,
            name=self.name,
            description=self.description,
            fields=list(self.fields),
        )

    def validate_inputs(self, values: dict[str, Any]) -> dict[str, Any]:
        expected = {field.name for field in self.fields}
        missing = [
            field.name
            for field in self.fields
            if field.required and field.name not in values and field.default is None
        ]
        unknown = sorted(set(values) - expected)
        if missing:
            raise TemplateInputError(f"Missing template inputs: {', '.join(missing)}")
        if unknown:
            raise TemplateInputError(f"Unknown template inputs: {', '.join(unknown)}")

        resolved = {
            field.name: values.get(field.name, field.default)
            for field in self.fields
        }
        for field in self.fields:
            value = resolved[field.name]
            if field.type == "select" and value not in field.options:
                raise TemplateInputError(
                    f"{field.name} must be one of: {', '.join(field.options)}"
                )
            if field.type == "number":
                try:
                    resolved[field.name] = int(value)
                except (TypeError, ValueError) as error:
                    raise TemplateInputError(f"{field.name} must be a number") from error
        return resolved


EXPLAIN_CONCEPT = PromptTemplateDefinition(
    id="explain-concept",
    name="Explain a concept",
    description="Explain a technical topic for a chosen experience level and style.",
    fields=(
        TemplateField(name="topic", label="Topic", type="text"),
        TemplateField(
            name="experience_level",
            label="Experience level",
            type="select",
            options=["beginner", "intermediate", "advanced"],
            default="beginner",
        ),
        TemplateField(
            name="response_style",
            label="Response style",
            type="select",
            options=["concise", "bullet points", "step by step"],
            default="concise",
        ),
        TemplateField(
            name="number_of_examples",
            label="Number of examples",
            type="number",
            default=2,
        ),
    ),
    prompt=ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an AI engineering tutor teaching a {experience_level} learner.",
            ),
            (
                "human",
                "Explain {topic}. Use a {response_style} response and include "
                "{number_of_examples} practical examples.",
            ),
        ]
    ),
)


TEMPLATES = {EXPLAIN_CONCEPT.id: EXPLAIN_CONCEPT}


def get_template(template_id: str) -> PromptTemplateDefinition:
    template = TEMPLATES.get(template_id)
    if template is None:
        raise TemplateNotFoundError(f"Unknown template_id: {template_id}")
    return template
