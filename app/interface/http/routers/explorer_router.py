"""New explorer router using Clean Architecture layers.

This replaces legacy `app/routers/explorer.py` for the explorer feature.
"""
from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from pathlib import Path

from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
from app.infrastructure.fs.timing_paths import TimingPaths
from app.interface.dependencies.explorer_dep import (
    get_list_directory_use_case, get_read_file_use_case, get_write_file_use_case
)
from app.application.explorer.use_cases import (
    ListDirectoryInput, ReadFileInput, WriteFileInput
)
from app.domain.explorer.errors import PathViolation as DomainPathViolation, PolicyViolation, FileNotFoundDomain

router = APIRouter(prefix="/api/explorer", tags=["explorer"])

# -------------------- Global root validation --------------------

def _validate_global_root(root: str) -> Path:
    p = Path(root)
    if not p.is_absolute():
        raise HTTPException(status_code=400, detail="Global root must be an absolute path")
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"Global root does not exist: {root}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Global root is not a directory: {root}")
    return p

# -------------------- Global Endpoints --------------------
@router.get("/global")
async def global_list(
    root: str = Query(..., description="Absolute root directory to browse"),
    path: Optional[str] = Query("", description="Relative path under root to list")
):
    try:
        root_path = _validate_global_root(root)
        uc = get_list_directory_use_case(str(root_path))
        out = uc.execute(ListDirectoryInput(relative=path or "", allow_external=False))
        return {
            "mode": "global",
            "root": str(root_path),
            "path": path or "",
            "entries": [e.__dict__ for e in out.entries]
        }
    except DomainPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/global/file")
async def global_read_file(
    root: str = Query(..., description="Absolute root directory"),
    path: str = Query(..., description="Relative file path under root")
):
    try:
        root_path = _validate_global_root(root)
        uc = get_read_file_use_case(str(root_path))
        out = uc.execute(ReadFileInput(relative=path, allow_external=False))
        fc = out.content
        resp = {
            "mode": "global",
            "root": str(root_path),
            "name": fc.name,
            "relative": fc.relative.value,
            "size": fc.size,
            "is_text": fc.is_text,
            "truncated": fc.truncated,
            "content": fc.content if fc.is_text else None,
        }
        if fc.excel:
            resp["excel_data"] = {s: sheet.__dict__ for s, sheet in fc.excel.sheets.items()}
            resp["sheet_names"] = fc.excel.sheet_names
        return resp
    except FileNotFoundDomain:
        raise HTTPException(status_code=404, detail="File not found")
    except DomainPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/global/file")
async def global_write_file(req: dict):
    try:
        root = req.get("root")
        path = req.get("path")
        content = req.get("content", "")
        if not root or not path:
            raise HTTPException(status_code=400, detail="root and path required")
        root_path = _validate_global_root(root)
        uc = get_write_file_use_case(str(root_path))
        out = uc.execute(WriteFileInput(relative=path, content=content))
        return {
            "mode": "global",
            "root": str(root_path),
            "path": path,
            "success": True,
            "message": "File saved successfully",
            "created": out.result.created
        }
    except (DomainPathViolation, PolicyViolation) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------------------- Project-scoped Endpoints --------------------
@router.get("/{project}/{subproject}")
async def project_list(project: str, subproject: str, path: Optional[str] = ""):
    try:
        from app.infrastructure.fs.timing_paths import TimingPaths
        tp = TimingPaths(project, subproject)
        if not tp.timing_root.exists():
            raise HTTPException(status_code=404, detail=f"Timing directory not found: {tp.timing_root}")
        uc = get_list_directory_use_case(str(tp.timing_root))
        out = uc.execute(ListDirectoryInput(relative=path or "", allow_external=True))
        return {
            "project": project,
            "subproject": subproject,
            "path": path or "",
            "root": str(tp.timing_root),
            "base_path": str(BASE_DIR),
            "entries": [e.__dict__ for e in out.entries]
        }
    except DomainPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project}/{subproject}/file")
async def project_read_file(project: str, subproject: str, path: str):
    try:
        tp = TimingPaths(project, subproject)
        if not tp.timing_root.exists():
            raise HTTPException(status_code=404, detail=f"Timing directory not found: {tp.timing_root}")
        uc = get_read_file_use_case(str(tp.timing_root))
        out = uc.execute(ReadFileInput(relative=path, allow_external=True))
        fc = out.content
        resp = {
            "project": project,
            "subproject": subproject,
            "path": path,
            "base_path": str(BASE_DIR),
            "name": fc.name,
            "relative": fc.relative.value,
            "size": fc.size,
            "is_text": fc.is_text,
            "truncated": fc.truncated,
            "content": fc.content if fc.is_text else None,
        }
        if fc.excel:
            resp["excel_data"] = {s: sheet.__dict__ for s, sheet in fc.excel.sheets.items()}
            resp["sheet_names"] = fc.excel.sheet_names
        return resp
    except FileNotFoundDomain:
        raise HTTPException(status_code=404, detail="File not found")
    except DomainPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project}/{subproject}/file")
async def project_write_file(project: str, subproject: str, req: dict):
    try:
        path = req.get("path")
        content = req.get("content", "")
        if not path:
            raise HTTPException(status_code=400, detail="path required")
        tp = TimingPaths(project, subproject)
        if not tp.timing_root.exists():
            raise HTTPException(status_code=404, detail=f"Timing directory not found: {tp.timing_root}")
        uc = get_write_file_use_case(str(tp.timing_root))
        out = uc.execute(WriteFileInput(relative=path, content=content))
        return {
            "project": project,
            "subproject": subproject,
            "path": path,
            "success": True,
            "message": "File saved successfully",
            "created": out.result.created
        }
    except (DomainPathViolation, PolicyViolation) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]
