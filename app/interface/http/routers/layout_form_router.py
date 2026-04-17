"""Reusable factory to create layout-form based routers.

Provides a thin adapter to render Jinja templates with auto-generated
form fields from a dataclass (e.g., wrap_up.FormConfig).
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from dataclasses import fields
from typing import get_origin, get_args, Literal, Type


_app_root = Path(__file__).resolve().parent.parent.parent.parent  # .../app
templates = Jinja2Templates(directory=str(_app_root / "presentation" / "templates"))


def _build_form_fields_from_dataclass(config) -> dict:
    form_fields = {}
    groups: dict[str, list] = {}
    for field in fields(config):
        if field.metadata.get("ui_hidden", False):
            continue
        field_name = field.name
        field_value = getattr(config, field_name)
        field_type = field.type
        label = field.metadata.get("label", field_name.replace("_", " ").title())
        optional = field.metadata.get("optional", False)
        placeholder = field.metadata.get("placeholder", "")
        ui_multi = field.metadata.get("ui_multi", False)
        is_checkbox = field.metadata.get("tick", False)
        editor = field.metadata.get("editor", False)
        exclude_option = field.metadata.get("exclude_option", False)
        # Support both legacy 'devide' and new 'divide' metadata keys
        divide = field.metadata.get("divide", field.metadata.get("devide"))
        group_name = field.metadata.get("group")
        origin = get_origin(field_type)
        if ui_multi and origin is list:
            form_fields[field_name] = {
                "type": "multi",
                "value": field_value if isinstance(field_value, list) else [],
                "label": label,
                "optional": optional,
                "placeholder": placeholder,
                "divide": divide,
                "exclude_option": exclude_option,
            }
            continue
        if origin is Literal:
            args = get_args(field_type)
            if args:
                form_fields[field_name] = {
                    "type": "literal",
                    "options": list(args),
                    "value": field_value,
                    "label": label,
                    "optional": optional,
                    "include_attribute": field.metadata.get("include_attribute", False),
                    "divide": divide,
                    "exclude_option": exclude_option,
                }
                continue
        if group_name:
            # Collect into group (support checkbox or other simple types)
            item_type = "checkbox" if (is_checkbox and (field_type == bool or isinstance(field_value, bool))) else (
                "int" if (field_type == int or isinstance(field_value, int)) else "text"
            )
            group_display = field.metadata.get("group_display", True)
            check_group = field.metadata.get("check_group", "")
            browser = field.metadata.get("browser", False)
            groups.setdefault(group_name, []).append({
                "name": field_name,
                "type": item_type,
                "value": field_value,
                "label": label,
                "placeholder": placeholder,
                "optional": optional,
                "group_display": group_display,
                "check_group": check_group,
                "browser": browser,
                "exclude_option": exclude_option,
            })
            continue
        if is_checkbox and (field_type == bool or isinstance(field_value, bool)):
            form_fields[field_name] = {
                "type": "checkbox",
                "value": bool(field_value),
                "label": label,
                "optional": optional,
                "divide": divide,
                "exclude_option": exclude_option,
            }
            continue
        if field_type == int or isinstance(field_value, int):
            form_fields[field_name] = {
                "type": "int",
                "value": field_value,
                "label": label,
                "optional": optional,
                "placeholder": placeholder,
                "divide": divide,
                "exclude_option": exclude_option,
            }
        else:
            browser = field.metadata.get("browser", False)
            form_fields[field_name] = {
                "type": "text",
                "value": field_value,
                "label": label,
                "optional": optional,
                "placeholder": placeholder,
                "editor": editor,
                "browser": browser,
                "divide": divide,
                "exclude_option": exclude_option,
            }
    # Attach groups at end
    for gname, items in groups.items():
        key = f"group__{gname.lower().replace(' ', '_')}"
        # Determine if group label should be displayed (default True unless any item sets False)
        group_display_any = any(item.get("group_display", True) for item in items)
        form_fields[key] = {
            "type": "group",
            "group_label": gname if group_display_any else "",
            "group_display": group_display_any,
            "group_fields": items,
        }
    return form_fields


def create_form_page_router(
    *,
    route_path: str,
    template_name: str,
    title: str,
    page_id: str,
    form_config_cls: Type,
) -> APIRouter:
    """Create an APIRouter for a form-based page.

    Args:
        route_path: URL path to mount (e.g., "/timing-qa-v2")
        template_name: Jinja template filename
        title: Page title to render in header
        page_id: Unique page identifier
        form_config_cls: Dataclass with `.default()` and field metadata

    Returns:
        APIRouter configured with a single GET endpoint.
    """
    router = APIRouter(tags=[page_id])

    @router.get(route_path, response_class=HTMLResponse)
    async def _page(request: Request):
        config = form_config_cls.default()
        form_fields = _build_form_fields_from_dataclass(config)
        hidden_fields = [
            (
                f.name, 
                getattr(config, f.name), 
                f.metadata.get("optional", False), 
                f.metadata.get("line_ending"),
                get_origin(f.type) is Literal,  # Detect if field is Literal type
                f.metadata.get("no_prefix", False)  # Detect if field should have no dash prefix
            ) 
            for f in fields(config) if f.metadata.get("ui_hidden", False)
        ]
        return templates.TemplateResponse(
            template_name,
            {
                "request": request,
                "title": title,
                "page_id": page_id,
                "form_fields": form_fields,
                "hidden_fields": hidden_fields,
            },
        )

    return router
