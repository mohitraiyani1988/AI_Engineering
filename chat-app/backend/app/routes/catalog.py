from fastapi import APIRouter

from app.models import get_model_definitions
from app.schemas import ModelOption, TemplateOption
from app.templates import TEMPLATES


router = APIRouter(tags=["catalog"])


@router.get("/models", response_model=list[ModelOption])
async def list_models() -> list[ModelOption]:
    return [
        definition.as_public_option()
        for definition in get_model_definitions().values()
    ]


@router.get("/templates", response_model=list[TemplateOption])
async def list_templates() -> list[TemplateOption]:
    return [template.as_public_option() for template in TEMPLATES.values()]
