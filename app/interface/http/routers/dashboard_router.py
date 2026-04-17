"""Dashboard router following Clean Architecture.

Thin HTTP layer handling navigation and page rendering.
Delegates business logic to application use cases.
"""
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import List, Tuple

from app.application.dashboard.use_cases import GetNavigationMenu
from app.interface.http.schemas.dashboard import NavigationMenuSchema, PageSchema
from app.interface.http.dependencies.dashboard import get_navigation_menu_uc

router = APIRouter()

# Template directory (Presentation layer)
_app_root = Path(__file__).resolve().parent.parent.parent.parent  # .../app
templates = Jinja2Templates(directory=str(_app_root / "presentation" / "templates"))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render a minimal home page instead of redirecting to Choose Project."""
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/api/navigation/pages", response_model=NavigationMenuSchema)
async def get_navigation_pages(
    nav_uc: GetNavigationMenu = Depends(get_navigation_menu_uc)
):
    """Get the list of available pages for navigation menu.
    
    Returns:
        NavigationMenuSchema with all available pages
    """
    menu = nav_uc.execute()
    pages_schema = [
        PageSchema(page_id=p.page_id, title=p.title)
        for p in menu.pages
    ]
    return NavigationMenuSchema(pages=pages_schema)


@router.get("/choose-project", response_class=HTMLResponse)
async def choose_project(
    request: Request,
    nav_uc: GetNavigationMenu = Depends(get_navigation_menu_uc)
):
    """Render the project selection landing page.
    
    Args:
        request: FastAPI request object
        nav_uc: Injected navigation menu use case
        
    Returns:
        Rendered HTML template
    """
    menu = nav_uc.execute()
    # Convert to legacy format for template compatibility
    pages_list: List[Tuple[str, str]] = [
        (p.page_id, p.title) for p in menu.pages
    ]
    return templates.TemplateResponse(
        "choose_project.html",
        {"request": request, "pages": pages_list}
    )


@router.get("/{page_id}", response_class=HTMLResponse)
async def render_page(
    page_id: str,
    request: Request,
    nav_uc: GetNavigationMenu = Depends(get_navigation_menu_uc)
):
    """Render a specific page by its ID.
    
    Args:
        page_id: URL-safe page identifier
        request: FastAPI request object
        nav_uc: Injected navigation menu use case
        
    Returns:
        Rendered HTML template
    """
    menu = nav_uc.execute()
    page = menu.get_page_by_id(page_id)
    
    # If page not found, return 404 or default
    if not page:
        # Fallback to generic page with the page_id as title
        title = page_id.replace("-", " ").title()
        pages_list = [(p.page_id, p.title) for p in menu.pages]
        return templates.TemplateResponse(
            "generic_page.html",
            {
                "request": request,
                "page_id": page_id,
                "title": title,
                "pages": pages_list
            }
        )
    
    # Convert to legacy format for template
    pages_list: List[Tuple[str, str]] = [
        (p.page_id, p.title) for p in menu.pages
    ]
    
    return templates.TemplateResponse(
        page.template_name,
        {
            "request": request,
            "pages": pages_list,
            "page_id": page_id,
            "title": page.title
        }
    )
