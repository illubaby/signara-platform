from __future__ import annotations

"""
Gantt router: minimal endpoint to append tasks into .cache/global_project_status.json.

Follows existing patterns: thin router, uses application file use cases for I/O.
"""

from fastapi import APIRouter, Body, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import logging
import os

from app.application.file_operations.use_cases import ReadFileContent, WriteFileContent
from app.infrastructure.p4.p4_path_repository import upload_file_to_p4, download_file_from_p4


logger = logging.getLogger(__name__)
router = APIRouter(tags=["gantt"])

# Setup templates for page rendering
app_root = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(app_root / "presentation" / "templates"))


# Page routes (no prefix)
@router.get("/gantt", response_class=HTMLResponse)
@router.get("/global-project-status", response_class=HTMLResponse)
def gantt_page(request: Request):
    """Render the Gantt chart page"""
    return templates.TemplateResponse("gantt.html", {"request": request})


def _cache_file_path() -> Path:
    # Use relative .cache path (same as per-project files)
    return Path(".cache") / "global_project_status.json"


# API routes
@router.post("/api/gantt/tasks")
def append_tasks(payload: dict = Body(...)):
    """
    Append new task milestones to global_project_status.json.

    Body format:
    {
      "task": "base-name",
      "etm_lead": "Name",
      "int_lead": "Name",
      "ckt_lead": "Name",
      "milestones": {
        "prelim": {"start": "YYYY-MM-DD", "end": "YYYY-MM-DD", "rel": "0.0_int"},
        "prefinal": {...},
        "final": {...},
        "swap_gds": {...}
      }
    }
    """
    try:
        task = (payload.get("task") or "").strip()
        if not task:
            raise HTTPException(status_code=400, detail="'task' is required")

        etm_lead = (payload.get("etm_lead") or "").strip()
        int_lead = (payload.get("int_lead") or "").strip()
        ckt_lead = (payload.get("ckt_lead") or "").strip()
        milestones = payload.get("milestones") or {}

        # Build entries to append
        items_to_add: list[dict] = []
        for key in ("prelim", "prefinal", "final", "swap_gds"):
            m = milestones.get(key) or {}
            start = (m.get("start") or "").strip()
            end = (m.get("end") or "").strip()
            rel = (m.get("rel") or "").strip()
            note = (m.get("note") or "").strip()
            if not start or not end:
                continue
            entry = {
                "task": task,
                "milestone": key,
                "etm_lead": etm_lead,
                "int_lead": int_lead,
                "ckt_lead": ckt_lead,
                "start": start,
                "end": end,
            }
            if rel:
                entry["rel"] = rel
            if note:
                entry["note"] = note
            items_to_add.append(entry)

        if not items_to_add:
            raise HTTPException(status_code=400, detail="No milestones with both start and end provided")

        cache_path = _cache_file_path()
        reader = ReadFileContent()
        writer = WriteFileContent()

        # Load existing array (if file missing or empty, start with empty list)
        data: list[dict]
        try:
            content = reader.execute(str(cache_path))
            # Handle empty file
            if not content or not content.strip():
                logger.warning(f"[Gantt] Empty file found at {cache_path}, initializing with empty array")
                data = []
            else:
                data = json.loads(content)
                if not isinstance(data, list):
                    raise ValueError("global_project_status.json is not a JSON array")
        except FileNotFoundError:
            logger.info(f"[Gantt] File not found at {cache_path}, creating new file")
            data = []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {cache_path}: {e}")
            # Initialize with empty array instead of failing
            logger.warning(f"[Gantt] Reinitializing corrupted file with empty array")
            data = []

        # Append and write back
        data.extend(items_to_add)
        new_content = json.dumps(data, indent=2)
        writer.execute(str(cache_path), new_content)

        logger.info(f"[Gantt] Added {len(items_to_add)} item(s) to {cache_path}")
        return {"added": len(items_to_add), "path": str(cache_path)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error appending tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/gantt/tasks/update")
def update_task(payload: dict = Body(...)):
    """
    Update an existing task milestone in global_project_status.json.
    
    Body format:
    {
      "id": "task-milestone-startdate",
      "task": "base-name",
      "milestone": "prelim",
      "start": "YYYY-MM-DD",
      "end": "YYYY-MM-DD",
      "rel": "0.5_int",
      "etm_lead": "Name",
      "int_lead": "Name",
      "ckt_lead": "Name",
      "note": "Optional note"
    }
    """
    try:
        logger.info(f"[Gantt] update_task received payload: {payload}")
        
        task_id = payload.get("id")
        if not task_id:
            raise HTTPException(status_code=400, detail="'id' is required")
        
        task = (payload.get("task") or "").strip()
        milestone = (payload.get("milestone") or "").strip()
        start = (payload.get("start") or "").strip()
        end = (payload.get("end") or "").strip()
        rel = (payload.get("rel") or "").strip()
        etm_lead = (payload.get("etm_lead") or "").strip()
        int_lead = (payload.get("int_lead") or "").strip()
        ckt_lead = (payload.get("ckt_lead") or "").strip()
        note = (payload.get("note") or "").strip()
        
        logger.info(f"[Gantt] Parsed note value: '{note}'")
        
        if not start or not end:
            raise HTTPException(status_code=400, detail="'start' and 'end' are required")

        cache_path = _cache_file_path()
        reader = ReadFileContent()
        writer = WriteFileContent()

        # Load existing data
        data: list[dict]
        try:
            content = reader.execute(str(cache_path))
            if not content or not content.strip():
                raise HTTPException(status_code=404, detail="No tasks found")
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValueError("global_project_status.json is not a JSON array")
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="No tasks file found")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {cache_path}: {e}")
            raise HTTPException(status_code=500, detail="Corrupt global_project_status.json")

        # Find and update the task
        updated = False
        for item in data:
            # Match by task name and milestone
            if item.get("task") == task and item.get("milestone") == milestone:
                item["start"] = start
                item["end"] = end
                if rel:
                    item["rel"] = rel
                else:
                    item.pop("rel", None)  # Remove if empty
                if etm_lead:
                    item["etm_lead"] = etm_lead
                if int_lead:
                    item["int_lead"] = int_lead
                if ckt_lead:
                    item["ckt_lead"] = ckt_lead
                if note:
                    item["note"] = note
                else:
                    item.pop("note", None)  # Remove if empty
                updated = True
                break

        if not updated:
            raise HTTPException(status_code=404, detail=f"Task not found: {task} - {milestone}")

        # Write back
        new_content = json.dumps(data, indent=2)
        writer.execute(str(cache_path), new_content)

        logger.info(f"[Gantt] Updated task: {task} - {milestone}")
        return {"success": True, "updated": f"{task} - {milestone}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/gantt/upload")
def upload_gantt_files(payload: dict = Body(default={})):
    """
    Upload global_project_status.json and timing_team.json to P4.
    Target depot: //wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/
    
    Body format (optional):
    {
      "changes": ["List of changes made during edit session"]
    }
    """
    try:
        changes = payload.get("changes", [])
        
        # Generate detailed description based on changes
        if changes:
            # Format the description with all changes
            change_details = "\n".join(f"- {change}" for change in changes)
            description = f"Update global project status from Gantt UI\n\nChanges:\n{change_details}"
        else:
            description = "Update global project status from Gantt UI"
        
        logger.info(f"[Gantt Upload] Uploading with description:\n{description}")
        
        # Use relative .cache path
        cache_dir = Path(".cache")
        
        status_file = cache_dir / "global_project_status.json"
        team_file = cache_dir / "timing_team.json"
        
        depot_base = "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing"
        status_depot = f"{depot_base}/global_project_status.json"
        team_depot = f"{depot_base}/timing_team.json"
        
        uploaded = []
        errors = []
        
        # Upload status file with detailed description
        if status_file.exists():
            success = upload_file_to_p4(
                str(status_file), 
                status_depot, 
                description=description
            )
            if success:
                uploaded.append("global_project_status.json")
            else:
                errors.append("Failed to upload global_project_status.json")
        else:
            errors.append("global_project_status.json not found")
        
        # Upload team file (if it exists, use same description)
        if team_file.exists():
            success = upload_file_to_p4(
                str(team_file), 
                team_depot, 
                description=description
            )
            if success:
                uploaded.append("timing_team.json")
            else:
                errors.append("Failed to upload timing_team.json")
        else:
            errors.append("timing_team.json not found")
        
        if errors:
            logger.warning(f"[Gantt Upload] Errors: {errors}")
        
        return {
            "uploaded": uploaded,
            "errors": errors,
            "success": len(errors) == 0
        }
    except Exception as e:
        logger.exception(f"Error uploading gantt files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/gantt/refresh")
def refresh_gantt_files():
    """
    Download global_project_status.json and timing_team.json from P4.
    Source depot: //wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/
    """
    try:
        # Use relative .cache path
        cache_dir = Path(".cache")
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        status_file = cache_dir / "global_project_status.json"
        team_file = cache_dir / "timing_team.json"
        
        depot_base = "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing"
        status_depot = f"{depot_base}/global_project_status.json"
        team_depot = f"{depot_base}/timing_team.json"
        
        downloaded = []
        errors = []
        
        # Download status file
        success = download_file_from_p4(status_depot, str(status_file))
        if success:
            downloaded.append("global_project_status.json")
        else:
            errors.append("Failed to download global_project_status.json")
        
        # Download team file
        success = download_file_from_p4(team_depot, str(team_file))
        if success:
            downloaded.append("timing_team.json")
        else:
            errors.append("Failed to download timing_team.json")
        
        if errors:
            logger.warning(f"[Gantt Refresh] Errors: {errors}")
        
        return {
            "downloaded": downloaded,
            "errors": errors,
            "success": len(errors) == 0
        }
    except Exception as e:
        logger.exception(f"Error refreshing gantt files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/api/gantt/projects/visibility")
def update_project_visibility(payload: dict = Body(...)):
    """
    Update the hidden status of projects in global_project_status.json.
    
    Body format:
    {
      "hiddenProjects": ["project-name-1", "project-name-2", ...]
    }
    """
    try:
        hidden_projects = set(payload.get("hiddenProjects") or [])
        logger.info(f"[Gantt] Updating project visibility. Hidden projects: {hidden_projects}")
        
        cache_path = _cache_file_path()
        reader = ReadFileContent()
        writer = WriteFileContent()
        
        # Load existing data
        data: list[dict]
        try:
            content = reader.execute(str(cache_path))
            if not content or not content.strip():
                data = []
            else:
                data = json.loads(content)
                if not isinstance(data, list):
                    raise ValueError("global_project_status.json is not a JSON array")
        except FileNotFoundError:
            data = []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from {cache_path}: {e}")
            data = []
        
        # Update hidden status for each task
        for item in data:
            task_name = item.get("task", "")
            if task_name in hidden_projects:
                item["hidden"] = True
            else:
                # Remove hidden field if project is visible
                item.pop("hidden", None)
        
        # Write back
        new_content = json.dumps(data, indent=2)
        writer.execute(str(cache_path), new_content)
        
        logger.info(f"[Gantt] Updated visibility for {len(hidden_projects)} hidden projects")
        return {"success": True, "hiddenCount": len(hidden_projects)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error updating project visibility: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
