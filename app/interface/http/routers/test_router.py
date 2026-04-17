
"""Test router: a tiny practice page for hello + fibonacci."""

from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.application.demo.use_cases import GetHelloFibonacci


@lru_cache
def _get_hello_fibonacci_uc() -> GetHelloFibonacci:
    return GetHelloFibonacci()

router = APIRouter()

_app_root = Path(__file__).resolve().parent.parent.parent.parent  # .../app
templates = Jinja2Templates(directory=str(_app_root / "presentation" / "templates"))

@router.get("/api/test-fibonacci")
async def api_test_fibonacci(uc: GetHelloFibonacci = Depends(_get_hello_fibonacci_uc)):
    msg, fib = uc.execute()
    return {"message": msg, "fibonacci": fib}

@router.get("/test", response_class=HTMLResponse)
async def test_page(request: Request, uc: GetHelloFibonacci = Depends(_get_hello_fibonacci_uc)):
    msg, fib = uc.execute()
    return templates.TemplateResponse(
        "test_page.html",
        {"request": request, "message": msg, "fibonacci": fib}
    )
