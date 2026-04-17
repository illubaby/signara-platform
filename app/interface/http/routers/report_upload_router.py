"""Report Upload Router"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel

from app.application.report_upload.use_cases import (
    UploadReportToP4,
    UploadReportInput,
)

router = APIRouter()
app_root = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(app_root / "presentation" / "templates"))


class UploadRequest(BaseModel):
    """Request model for file upload."""
    local_path: str
    depot_path: str
    description: str = ""


@router.get("/report-upload", response_class=HTMLResponse)
def report_upload_page(request: Request):
    """Render report upload page."""
    return templates.TemplateResponse("report_upload.html", {"request": request})


@router.post("/api/report-upload")
async def upload_report(request: UploadRequest):
    """Upload a report file to Perforce depot."""
    try:
        use_case = UploadReportToP4()
        result = use_case.execute(UploadReportInput(
            local_path=request.local_path,
            depot_path=request.depot_path,
            description=request.description or f"Upload {Path(request.local_path).name}"
        ))
        
        return {
            "success": result.success,
            "message": result.message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
