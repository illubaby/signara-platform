"""Internal Timing v2 page router."""
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(tags=["internal-timing-v2"])
_app_root = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(_app_root / "presentation" / "templates"))


@router.get("/internal-timing-v2", response_class=HTMLResponse)
async def internal_timing_v2_page(request: Request):
    return templates.TemplateResponse(
        "internal_timing_v2.html",
        {
            "request": request,
            "title": "Internal Timing v2",
            "page_id": "internal-timing-v2",
        },
    )
