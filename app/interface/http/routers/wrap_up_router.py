"""Project router following Clean Architecture.

Thin HTTP layer handling collect depot page rendering.
Delegates business logic to application use cases.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dataclasses import fields
from typing import get_origin, get_args, Literal

from app.domain.wrap_up.entities import FormConfig

router = APIRouter(tags=["wrap_up"])

# Template directory (Presentation layer)
_app_root = Path(__file__).resolve().parent.parent.parent.parent  # .../app
templates = Jinja2Templates(directory=str(_app_root / "presentation" / "templates"))


def _build_form_fields_from_dataclass(config: FormConfig) -> dict:
    """Auto-generate form fields from dataclass introspection."""
    form_fields = {}
    
    for field in fields(config):
        # Skip fields marked as ui_hidden
        if field.metadata.get("ui_hidden", False):
            continue
            
        field_name = field.name
        field_value = getattr(config, field_name)
        field_type = field.type
        
        # Get custom label from metadata, fallback to title-cased field name
        label = field.metadata.get("label", field_name.replace("_", " ").title())
        optional = field.metadata.get("optional", False)
        placeholder = field.metadata.get("placeholder", "")
        ui_multi = field.metadata.get("ui_multi", False)
        
        # Check if it's a multi-value field (list type with ui_multi metadata)
        origin = get_origin(field_type)
        if ui_multi and origin is list:
            form_fields[field_name] = {
                "type": "multi",
                "value": field_value if isinstance(field_value, list) else [],
                "label": label,
                "optional": optional,
                "placeholder": placeholder
            }
            continue
        
        # Check if it's a Literal type
        if origin is Literal:
            args = get_args(field_type)
            if args:
                form_fields[field_name] = {
                    "type": "literal",
                    "options": list(args),
                    "value": field_value,
                    "label": label,
                    "optional": optional
                }
                continue
        
        # Check for int/str types
        if field_type == int or isinstance(field_value, int):
            form_fields[field_name] = {
                "type": "int",
                "value": field_value,
                "label": label,
                "optional": optional,
                "placeholder": placeholder
            }
        else:
            form_fields[field_name] = {
                "type": "text",
                "value": field_value,
                "label": label,
                "optional": optional,
                "placeholder": placeholder
            }
    
    return form_fields


@router.get("/wrap-up", response_class=HTMLResponse)
@router.get("/project-wrap-up", response_class=HTMLResponse)
async def wrap_up_page(request: Request):
    """Render the project wrap-up page.
    
    Args:
        request: FastAPI request object
        
    Returns:
        HTMLResponse template with auto-generated form fields
    """
    config = FormConfig.default()
    form_fields = _build_form_fields_from_dataclass(config)
    
    # Extract hidden fields with their default values
    hidden_fields = [(f.name, getattr(config, f.name)) for f in fields(config) if f.metadata.get("ui_hidden", False)]
    
    return templates.TemplateResponse(
        "wrap_up.html",
        {
            "request": request,
            "title": "Wrap-up",
            "page_id": "wrap-up",
            "form_fields": form_fields,
            "hidden_fields": hidden_fields,
        }
    )
