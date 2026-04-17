from fastapi import APIRouter, Depends, HTTPException
from app.application.cell.use_cases import (
    PrepareIntCell, PrepareIntCellInput, PrepareIntCellOutput,
    GetCellPvtStatus, GetCellPvtStatusInput
)
from app.application.cell.sync_use_cases import SyncIntNetlist, SyncIntNetlistInput, SyncIntNetlistOutput
from app.application.cell.netlist_use_cases import IntNetlistVersion, IntNetlistVersionInput, IntNetlistVersionOutput
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
from app.domain.common.validation import validate_component, ValidationError
from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.infrastructure.fs.symlink_service import SymlinkService
from pathlib import Path

router = APIRouter(prefix="/api/cell", tags=["cell"])

def get_prepare_int_cell_uc() -> PrepareIntCell:
    return PrepareIntCell(SafPerforceRepositoryP4())

def get_sync_int_netlist_uc() -> SyncIntNetlist:
    return SyncIntNetlist()

def get_int_netlist_version_uc() -> IntNetlistVersion:
    return IntNetlistVersion()

def get_cell_pvt_status_uc() -> GetCellPvtStatus:
    return GetCellPvtStatus()

@router.post("/{project}/{subproject}/int/{cell_base}/prepare", response_model=PrepareIntCellOutput)
async def prepare_int_cell(project: str, subproject: str, cell_base: str, uc: PrepareIntCell = Depends(get_prepare_int_cell_uc)):
    for v, f in ((project, "project"), (subproject, "subproject"), (cell_base, "cell")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    out = uc.execute(PrepareIntCellInput(project=project, subproject=subproject, cell_base=cell_base))
    if not out.synced:
        # Return 202 Accepted if directory created but sync failed (non-fatal)
        return out
    return out

__all__ = ["router"]

# --- Internal Timing support: ensure NT share symlink/junction ---

@router.post("/{project}/{subproject}/nt/ensure-share")
async def ensure_nt_share(project: str, subproject: str):
    """Ensure nt/share links to the remote canonical share path.

    Returns created/note/error with resolved nt_root for UI feedback.
    """
    for v, f in ((project, "project"), (subproject, "subproject")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

    try:
        nt_root: Path = PROJECTS_BASE / project / subproject / "design" / "timing" / "nt"
        nt_root.mkdir(parents=True, exist_ok=True)

        svc = SymlinkService()
        res = svc.ensure_nt_share_link(project, subproject, nt_root)
        return {
            "project": project,
            "subproject": subproject,
            "nt_root": str(nt_root),
            "created": bool(res.get("created", False)),
            "note": res.get("note", ""),
            "error": res.get("error"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ensure NT share: {e}")

# --- Internal Timing support: sync INT netlist from extraction path ---

@router.post("/{project}/{subproject}/int/{cell}/sync-netlist", response_model=SyncIntNetlistOutput)
async def sync_int_netlist(project: str, subproject: str, cell: str, uc: SyncIntNetlist = Depends(get_sync_int_netlist_uc)):
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    out = uc.execute(SyncIntNetlistInput(project=project, subproject=subproject, cell=cell))
    return out

@router.get("/{project}/{subproject}/int/{cell}/netlist-version", response_model=IntNetlistVersionOutput)
async def int_netlist_version(project: str, subproject: str, cell: str, uc: IntNetlistVersion = Depends(get_int_netlist_version_uc)):
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    out = uc.execute(IntNetlistVersionInput(project=project, subproject=subproject, cell=cell))
    return out

@router.get("/{project}/{subproject}/int/{cell}/pvt-status")
async def int_pvt_status(project: str, subproject: str, cell: str, uc: GetCellPvtStatus = Depends(get_cell_pvt_status_uc)):
    """Get PVT status summary for an internal timing NT cell."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # INT cells have _int suffix in the directory name
    cell_with_suffix = f"{cell}_int" if not cell.endswith("_int") else cell
    
    # Use the GetCellPvtStatus use case for NT cells
    out = uc.execute(GetCellPvtStatusInput(
        project=project,
        subproject=subproject,
        cell=cell_with_suffix,
        cell_type="nt"
    ))
    
    return {
        "project": project,
        "subproject": subproject,
        "cell": cell,
        "summary": out.summary
    }

@router.get("/{project}/{subproject}/int/{cell}/report-exists")
async def int_report_exists(project: str, subproject: str, cell: str):
    """Check if Internal Timing Report Excel file exists for the cell."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        try:
            validate_component(v, f)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    # Remove _int suffix for path construction
    cell_base = cell[:-4] if cell.endswith("_int") else cell
    
    # Path: <Base>/<project>/<subproject>/design/timing/quality/7_internal/<cell>/<cell>_InternalTiming_Report.xlsx
    report_path = PROJECTS_BASE / project / subproject / "design" / "timing" / "quality" / "7_internal" / cell_base / f"{cell_base}_InternalTiming_Report.xlsx"
    
    exists = report_path.exists()
    
    return {
        "project": project,
        "subproject": subproject,
        "cell": cell,
        "exists": exists,
        "path": str(report_path) if exists else None
    }

