"""Checklist router following Clean Architecture."""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.application.checklist.use_cases import GetChecklist, SaveChecklist
from app.domain.checklist.entities import Checklist
from app.infrastructure.logging.logging_config import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/api/checklist")
async def get_checklist(project: str, refresh: bool = False):
    """
    Get checklist for a project.
    
    Args:
        project: Project name
        refresh: If True, download latest from P4
        
    Returns:
        JSON checklist data
    """
    logger.info(f"[get_checklist] GET /api/checklist?project={project}&refresh={refresh}")
    
    if not project:
        raise HTTPException(status_code=400, detail="Project parameter is required")
    
    try:
        use_case = GetChecklist()
        checklist = use_case.execute(project, refresh)
        
        if not checklist:
            raise HTTPException(status_code=404, detail=f"Checklist not found for project: {project}")
        
        return {"data": checklist.to_dict()}
        
    except Exception as e:
        logger.error(f"[get_checklist] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/checklist")
async def save_checklist(payload: dict):
    """
    Save checklist for a project.
    
    Body:
        {
            "project": "project_name",
            "data": [...checklist sections...]
        }
        
    Returns:
        Success status
    """
    logger.info(f"[save_checklist] POST /api/checklist")
    
    project = payload.get("project")
    data = payload.get("data")
    
    if not project:
        raise HTTPException(status_code=400, detail="Project parameter is required")
    
    if not data:
        raise HTTPException(status_code=400, detail="Checklist data is required")
    
    try:
        checklist = Checklist.from_dict(data)
        use_case = SaveChecklist()
        
        if use_case.execute(project, checklist):
            return {"success": True, "message": "Checklist saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save checklist")
            
    except Exception as e:
        logger.error(f"[save_checklist] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
