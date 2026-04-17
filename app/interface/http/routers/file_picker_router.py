"""File picker router using Clean Architecture layers.

Provides HTTP endpoints for browsing and selecting files/folders.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pathlib import Path

from app.interface.dependencies.file_picker_dep import (
    get_browse_directory_use_case,
    get_validate_path_use_case,
)
from app.interface.http.schemas.file_picker import (
    BrowseDirectoryRequest,
    BrowseDirectoryResponse,
    ValidatePathRequest,
    ValidatePathResponse,
    PickerEntrySchema,
)
from app.application.file_picker.use_cases import (
    BrowseDirectoryInput,
    ValidatePathInput,
)
from app.domain.file_picker.errors import PathViolation, AccessDenied
from app.infrastructure.fs.project_root import PROJECTS_BASE

router = APIRouter(prefix="/api/file-picker", tags=["file-picker"])

# Setup templates
app_root = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(app_root / "presentation" / "templates"))



@router.get("/example", response_class=HTMLResponse)
async def file_picker_example_page(request: Request):
    """Render the simple file picker integration example page."""
    return templates.TemplateResponse(
        "file_picker_example.html",
        {"request": request}
    )


@router.post("/browse", response_model=BrowseDirectoryResponse)
async def browse_directory(
    req: BrowseDirectoryRequest,
    use_case=Depends(get_browse_directory_use_case)
):
    """Browse a directory and return its contents.
    
    Args:
        req: Request containing the path to browse
        use_case: Injected BrowseDirectory use case
        
    Returns:
        Directory contents with entries sorted (folders first)
        
    Raises:
        HTTPException: 400 for invalid paths, 403 for access denied, 500 for other errors
    """
    try:
        inp = BrowseDirectoryInput(path=req.path)
        out = use_case.execute(inp)
        
        return BrowseDirectoryResponse(
            current_path=out.current_path,
            parent_path=out.parent_path,
            entries=[
                PickerEntrySchema(
                    name=e.name,
                    path=e.path,
                    is_dir=e.is_dir,
                    is_symlink=e.is_symlink,
                    size=e.size,
                    modified_time=e.modified_time
                )
                for e in out.entries
            ]
        )
    except PathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AccessDenied as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=ValidatePathResponse)
async def validate_path(
    req: ValidatePathRequest,
    use_case=Depends(get_validate_path_use_case)
):
    """Validate if a path exists and is accessible.
    
    Args:
        req: Request containing the path to validate
        use_case: Injected ValidatePath use case
        
    Returns:
        Validation result indicating if path is valid and whether it's a directory
    """
    try:
        inp = ValidatePathInput(path=req.path)
        out = use_case.execute(inp)
        
        return ValidatePathResponse(
            is_valid=out.is_valid,
            is_directory=out.is_directory,
            error_message=out.error_message
        )
    except Exception as e:
        return ValidatePathResponse(
            is_valid=False,
            is_directory=False,
            error_message=str(e)
        )


@router.get("/default-path")
async def get_default_path(project: str | None = None, subproject: str | None = None):
    """Get a default starting path appropriate for the server's OS.
    
    If project and subproject are provided, returns <PROJECTS_BASE>/<project>/<subproject>/design/timing/
    Otherwise falls back to C:/ (Windows) or ~ (Linux/macOS)
    
    Args:
        project: Optional project name from AppSelection
        subproject: Optional subproject name from AppSelection
    
    Returns:
        A dictionary with the default path for browsing
    """
    import os
    import platform
    
    system = platform.system()
    
    # If project and subproject are provided, use project-based path
    if project and subproject:
        timing_path = PROJECTS_BASE / project / subproject / "design" / "timing"
        if timing_path.exists():
            default_path = str(timing_path)
        else:
            # Fallback to project/subproject root if timing dir doesn't exist
            project_path = PROJECTS_BASE / project / subproject
            if project_path.exists():
                default_path = str(project_path)
            else:
                # Fallback to PROJECTS_BASE if project doesn't exist
                default_path = str(PROJECTS_BASE)
    else:
        # No project context: use system defaults
        if system == "Windows":
            default_path = "C:/"
        else:
            default_path = os.path.expanduser("~")
    
    return {
        "path": default_path,
        "system": system
    }


__all__ = ["router"]
