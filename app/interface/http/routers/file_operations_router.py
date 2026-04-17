"""
Interface layer: HTTP router for file operations.

Thin adapter that translates HTTP requests to use case calls.
Handles API endpoints for opening files with external applications.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Body
from typing import Optional
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

from app.interface.http.schemas.file_operations import OpenFileRequest, OpenFileResponse
from app.interface.http.dependencies.file_operations import (
    get_open_file_use_case,
    get_prepare_file_download_use_case,
)
from app.application.file_operations.use_cases import OpenFileWithDefaultApp, PrepareFileDownload, CreateFileSimple
from app.infrastructure.fs.symlink_service import SymlinkService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["File Operations"])

# Setup Jinja2 templates
_app_root = Path(__file__).resolve().parent.parent.parent.parent
_templates_dir = _app_root / "presentation" / "templates"
templates = Jinja2Templates(directory=str(_templates_dir))


@router.get("/test-file-operations", response_class=HTMLResponse)
async def test_file_operations_page(request: Request):
    """
    Render the test page for file operations feature.
    
    This page allows developers to test opening files with their default applications.
    """
    return templates.TemplateResponse("test_open_file.html", {"request": request})


@router.post("/api/files/open", response_model=OpenFileResponse)
def open_file_with_default_app(
    request: OpenFileRequest,
    use_case: OpenFileWithDefaultApp = Depends(get_open_file_use_case)
):
    """
    Open a file with its default system application.
    
    **Examples:**
    - Excel files (.xlsx, .xls) will open in Microsoft Excel
    - Word documents (.docx, .doc) will open in Microsoft Word
    - PDF files will open in the default PDF viewer
    - Text files will open in the default text editor
    
    **Request Body:**
    ```json
    {
        "file_path": "C:\\path\\to\\file.xlsx"
    }
    ```
    
    **Response:**
    ```json
    {
        "status": "success",
        "message": "Successfully opened: file.xlsx"
    }
    ```
    """
    try:
        logger.info(f"API: Opening file: {request.file_path}")
        result = use_case.execute(request.file_path)
        return OpenFileResponse(**result)
        
    except FileNotFoundError as e:
        logger.warning(f"File not found: {request.file_path}")
        raise HTTPException(
            status_code=404, 
            detail=f"File not found: {str(e)}"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid input: {str(e)}")
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file path: {str(e)}"
        )
        
    except PermissionError as e:
        logger.error(f"Permission denied: {str(e)}")
        raise HTTPException(
            status_code=403, 
            detail=f"Permission denied: {str(e)}"
        )
        
    except RuntimeError as e:
        logger.error(f"Failed to open file: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to open file: {str(e)}"
        )
        
    except Exception as e:
        logger.exception(f"Unexpected error opening file: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )


@router.get("/api/html-viewer/{filename:path}")
def view_html_with_context(
    filename: str,
    request: Request,
    html_dir: Optional[str] = None,
):
    """Generic HTML viewer that serves HTML files with proper path context.
    
    This endpoint serves HTML files from a specified directory so relative links work.
    All relative links within the HTML will be resolved correctly.
    
    Query Parameters:
        html_dir: Absolute path to the HTML directory
        
    Path Parameters:
        filename: HTML filename relative to html_dir (can include subdirectories)
    
    Returns:
        HTML file response rendered in browser
        
    Example:
        GET /api/html-viewer/summary.html?html_dir=/path/to/html
        GET /api/html-viewer/details/report.html?html_dir=/path/to/html
    """
    try:
        from pathlib import Path
        
        # If html_dir was not provided, try to infer it from the Referer query string
        if not html_dir and request:
            try:
                from urllib.parse import urlparse, parse_qs
                ref = request.headers.get("referer")
                if ref:
                    qs = parse_qs(urlparse(ref).query)
                    html_dir = (qs.get("html_dir") or [None])[0]
                    logger.debug(f"[HTML Viewer] Inferred html_dir from Referer: {html_dir}")
            except Exception:
                # Fall through to error handling below if we cannot infer
                pass

        # If still missing, use cookie from prior viewer loads
        if not html_dir and request:
            cookie_dir = request.cookies.get("html_viewer_dir")
            if cookie_dir:
                html_dir = cookie_dir
                logger.debug(f"[HTML Viewer] Using cookie html_viewer_dir: {html_dir}")

        if not html_dir:
            # Maintain validation-style error when html_dir is missing
            raise HTTPException(status_code=422, detail=[{"type":"missing","loc":["query","html_dir"],"msg":"Field required","input":None}])

        # Convert html_dir to Path object
        logger.debug(f"[HTML Viewer] Incoming request filename={filename}, html_dir={html_dir}")
        base_dir = Path(html_dir).expanduser().resolve()
        logger.debug(f"[HTML Viewer] Resolved base_dir={base_dir}")

        # If original request omitted html_dir but we inferred it, redirect to canonical URL with query appended
        try:
            if request and request.query_params.get("html_dir") is None and html_dir:
                canonical = f"/api/html-viewer/{filename}?html_dir={str(base_dir)}"
                logger.debug(f"[HTML Viewer] Redirecting to canonical URL: {canonical}")
                return RedirectResponse(url=canonical, status_code=307)
        except Exception:
            # Non-fatal if redirect cannot be performed
            logger.debug("[HTML Viewer] Failed to perform canonical redirect")
        
        # Construct full file path
        file_path = base_dir / filename
        
        # Security check: ensure the resolved path is within the html directory
        resolved_path = file_path.resolve()
        logger.debug(f"[HTML Viewer] Target resolved_path={resolved_path}")
        if not str(resolved_path).startswith(str(base_dir)):
            raise HTTPException(status_code=403, detail="Access denied: path traversal detected")
        
        # Check if file exists; add small fallbacks for common summary filenames
        if not resolved_path.exists():
            logger.info(f"[HTML Viewer] File not found: {resolved_path}, attempting fallbacks if applicable")
            # If requesting summary.html, try index.html or Summary.html as fallbacks
            fallback_path = None
            try:
                if filename.lower() == "summary.html":
                    idx = base_dir / "index.html"
                    summ_cap = base_dir / "Summary.html"
                    if idx.exists():
                        fallback_path = idx.resolve()
                        logger.info(f"[HTML Viewer] Using index.html fallback: {fallback_path}")
                    elif summ_cap.exists():
                        fallback_path = summ_cap.resolve()
                        logger.info(f"[HTML Viewer] Using Summary.html fallback: {fallback_path}")
                # Provide more context in error if still missing
                if fallback_path is None:
                    logger.error(f"[HTML Viewer] No fallback available for {filename}; checked path={resolved_path}")
                    raise HTTPException(status_code=404, detail=f"File not found: {filename} at {resolved_path}")
            except HTTPException:
                raise
            except Exception:
                # If any unexpected error, still return a clear 404
                logger.exception(f"[HTML Viewer] Unexpected error while evaluating fallbacks for {filename}")
                raise HTTPException(status_code=404, detail=f"File not found: {filename} at {resolved_path}")
            # Serve the fallback
            resolved_path = fallback_path
            logger.debug(f"[HTML Viewer] Serving fallback path: {resolved_path}")
        
        if not resolved_path.is_file():
            raise HTTPException(status_code=400, detail=f"Not a file: {filename}")
        
        logger.info(f"API: Serving HTML from viewer: {resolved_path}")
        
        # Serve with text/html so browser renders it
        response = FileResponse(
            path=str(resolved_path),
            media_type="text/html",
        )
        # Persist html_dir for subsequent in-page links without query params
        try:
            response.set_cookie(
                key="html_viewer_dir",
                value=str(base_dir),
                max_age=3600,  # 1 hour
                path="/",
                httponly=False,
                secure=False,
                samesite="lax",
            )
        except Exception:
            # Non-fatal if cookie cannot be set
            logger.debug("[HTML Viewer] Failed to set cookie html_viewer_dir")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error serving HTML via viewer")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.get("/api/files/view-html")
def view_html_file(
    file_path: str,
    use_case: PrepareFileDownload = Depends(get_prepare_file_download_use_case)
):
    """View an HTML file in the browser (renders instead of downloading).

    Query Parameters:
        file_path: Path to the HTML file on the server.

    Returns:
        HTML file response with text/html content type for browser rendering.
    """
    try:
        meta = use_case.execute(file_path)
        abs_path = meta["absolute_path"]
        logger.info(f"API: Serving HTML file for viewing: {abs_path}")
        # Serve with text/html so browser renders it instead of downloading
        return FileResponse(
            path=abs_path,
            media_type="text/html",
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error viewing HTML file")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.get("/api/files/download")
def download_file(
    file_path: str,
    use_case: PrepareFileDownload = Depends(get_prepare_file_download_use_case)
):
    """Download a file from the server so the client (Windows) can open it locally.

    Query Parameters:
        file_path: Path to the file on the server.

    Returns:
        Streamed file response with appropriate headers.

    Notes:
        The browser controls whether the file auto-opens after download. Excel / Word
        typically prompt or open based on user settings. We cannot force native app
        execution from the server for security reasons.
    """
    try:
        meta = use_case.execute(file_path)
        abs_path = meta["absolute_path"]
        filename = meta["filename"]
        logger.info(f"API: Downloading file {abs_path}")
        # Let FastAPI stream the file. content_type left None to allow auto-detect.
        return FileResponse(
            path=abs_path,
            filename=filename,
            media_type="application/octet-stream",  # generic; browser may override for known types
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error preparing download")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.post("/api/files/symlinks")
def create_cell_symlinks(request: dict = Body(...)):
    """Create symlinks (TimingCloseBeta.py and bin/) in cell directory."""
    try:
        cell_root = request.get("cell_root")
        if not cell_root:
            raise HTTPException(status_code=400, detail="cell_root is required")
        service = SymlinkService()
        result = service.link_cell_tools(Path(cell_root))
        return {"success": True, "note": result.note, "warnings": result.warnings}
    except Exception as e:
        logger.error(f"Symlink error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']


@router.post("/api/files/create")
def create_simple_file(payload: dict = Body(...)):
    """Create a file if missing. Body: {"dir": "path", "filename": "name"}.
    Returns {"created": bool, "path": full_path}.
    """
    dir_path = payload.get("dir")
    filename = payload.get("filename")
    content = payload.get("content")
    if not dir_path or not filename:
        raise HTTPException(status_code=400, detail="dir and filename required")
    use_case = CreateFileSimple()
    try:
        created = use_case.execute(dir_path, filename, content)
        full_path = str(Path(dir_path).expanduser().resolve() / filename)
        return {"created": created, "path": full_path}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error creating file")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/files/read")
def read_file_content(payload: dict = Body(...)):
    """Read file content. Body: {"path": "file_path"}.
    Returns {"content": file_content}.
    """
    from app.application.file_operations.use_cases import ReadFileContent
    
    file_path = payload.get("path")
    if not file_path:
        raise HTTPException(status_code=400, detail="path is required")
    
    use_case = ReadFileContent()
    try:
        content = use_case.execute(file_path)
        return {"content": content}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error reading file")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/files/write")
def write_file_content(payload: dict = Body(...)):
    """Write content to file. Body: {"path": "file_path", "content": "file_content"}.
    Returns {"success": true}.
    """
    from app.application.file_operations.use_cases import WriteFileContent
    
    file_path = payload.get("path")
    content = payload.get("content", "")
    
    if not file_path:
        raise HTTPException(status_code=400, detail="path is required")
    
    use_case = WriteFileContent()
    try:
        use_case.execute(file_path, content)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error writing file")
        raise HTTPException(status_code=500, detail=str(e))
