"""New SAF router following Clean Architecture layering (Phase 3+).

Endpoints:
GET /api/saf/{project}/{subproject}/cells?type=sis|nt
POST /api/saf/{project}/{subproject}/{cell}/sync-inst?type=sis|nt
GET /api/saf/{project}/{subproject}/pvts
GET /api/saf/{project}/{subproject}/cells/{cell}/nt-pvts
WS /api/saf/{project}/{subproject}/cells/{cell}/execute/ws (real-time streaming)
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query, Body, WebSocket
from typing import List, Optional
from pathlib import Path
import logging
from app.interface.http.schemas.saf import CellDTO, CellListDTO, CellInfo, CellList, SyncInstStatusDTO, PVTListResponse, PVTStatusResponse, DiagnoseResult, TaskQueueStatus, TaskQueueRequest, TaskQueueResult, PosteditLibCountResult, PostQALibCountResult, NetlistSyncResult, FileListResponse, FileReadResponse, FileWriteRequest, FileWriteResponse, PostEditDefaults, PostEditRequest, PostEditResult, JobRequest, JobResult
from app.infrastructure.websocket.stream_executor import WebSocketStreamExecutor
from app.application.saf.use_cases import (
    SyncInstFile, SyncInstFileInput,
    GetPvtStatuses, GetPvtStatusesInput,
)
from app.application.saf.list_and_diagnose_use_cases import (
    ListSafCells, ListSafCellsInput,
    DiagnoseSaf, DiagnoseSafInput
)
from app.application.saf.pvt_use_cases import (
    GetPvtList, GetPvtListInput,
    GetNtPvtList, GetNtPvtListInput,
)
from app.application.saf.task_queue_use_cases import (
    GetTaskQueueStatus, GetTaskQueueStatusInput,
    WriteTaskQueue, WriteTaskQueueInput,
)
from app.application.saf.saf_library_use_cases import (
    CountPosteditLibs, CountPosteditLibsInput,
    CountPostqaLibs, CountPostqaLibsInput,
)
from app.application.saf.netlist_use_cases import (
    SyncNetlist, SyncNetlistInput,
    GetNetlistDebug, GetNetlistDebugInput,
)
from app.application.saf.file_operations_use_cases import (
    ListPvtFiles, ListPvtFilesInput,
    ReadPvtFile, ReadPvtFileInput,
    WritePvtFile, WritePvtFileInput,
)
from app.application.saf.post_edit_use_cases import (
    GetPostEditDefaults, GetPostEditDefaultsInput,
    RunPostEdit, RunPostEditInput,
)
from app.application.saf.prepare_run_use_case import (
    PrepareAndRunJob, PrepareAndRunJobInput,
)
from app.domain.saf.entities import Cell
from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS
from app.application.cell.use_cases import list_local_int_cells
from app.infrastructure.fs.pvt_status_repository_fs import PvtStatusRepositoryFS
from app.application.file_operations.use_cases import CountLibFilesInDirectory
from app.application.pvt.use_case import MergePVTMode
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.domain.common.validation import validate_component, ValidationError
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/saf", tags=["saf"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Dependency factories (simple inline for now; will move to dependencies module later)

def get_list_saf_cells_uc() -> ListSafCells:
    from app.application.saf.ttl_cache import TTLCache
    return ListSafCells(SafCellRepositoryFS(), SafPerforceRepositoryP4(), TTLCache(ttl_seconds=300))

def get_sync_inst_file_uc() -> SyncInstFile:
    return SyncInstFile(SafPerforceRepositoryP4())

def get_diagnose_saf_uc() -> DiagnoseSaf:
    return DiagnoseSaf(SafCellRepositoryFS())

def get_task_queue_status_uc() -> GetTaskQueueStatus:
    return GetTaskQueueStatus(SafCellRepositoryFS())

def write_task_queue_uc() -> WriteTaskQueue:
    return WriteTaskQueue(SafCellRepositoryFS())

def get_count_postedit_libs_uc() -> CountPosteditLibs:
    return CountPosteditLibs()

def get_count_postqa_libs_uc() -> CountPostqaLibs:
    return CountPostqaLibs()

def get_sync_netlist_uc() -> SyncNetlist:
    from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
    return SyncNetlist(SafPerforceRepositoryP4())

@router.get("/{project}/{subproject}/cells-int")
async def list_int_cells(project: str, subproject: str):
    """Return cells from List_cell_INT (treated as SiS) directly from ProjectInfo.xlsx."""
    for v, f in ((project, "project"), (subproject, "subproject")):
        _validate_component(v, f)
    p4_repo = SafPerforceRepositoryP4()
    depot_cells = p4_repo.list_int_cells(project, subproject)
    # Use application-level helper to avoid infra changes
    local_cells = list_local_int_cells(project, subproject)
    # Merge unique, prefer sorted order
    merged = sorted(set(depot_cells) | set(local_cells))
    return {"project": project, "subproject": subproject, "cells": merged}

def get_netlist_debug_uc() -> GetNetlistDebug:
    return GetNetlistDebug(SafCellRepositoryFS())

def get_list_pvt_files_uc() -> ListPvtFiles:
    return ListPvtFiles(SafCellRepositoryFS())

def get_read_pvt_file_uc() -> ReadPvtFile:
    return ReadPvtFile(SafCellRepositoryFS())

def get_write_pvt_file_uc() -> WritePvtFile:
    return WritePvtFile(SafCellRepositoryFS())

def get_postedit_defaults_uc() -> GetPostEditDefaults:
    return GetPostEditDefaults()

def get_run_postedit_uc() -> RunPostEdit:
    return RunPostEdit()

def prepare_and_run_job_uc() -> PrepareAndRunJob:
    return PrepareAndRunJob()

@router.get("/{project}/{subproject}/cells", response_model=CellList)
async def list_cells(
    project: str,
    subproject: str,
    debug: bool = Query(False, description="Return path resolution debug info"),
    force_refresh: bool = Query(False, description="Bypass cache and rescan"),
    uc: ListSafCells = Depends(get_list_saf_cells_uc)
):
    """List all SAF cells (SiS and NT) with PVT status (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject")):
        _validate_component(v, f)
    
    # Use the enhanced use case that handles both SiS and NT
    out = uc.execute(ListSafCellsInput(project=project, subproject=subproject, force_refresh=force_refresh))
    
    # Enrich with PVT status summary
    status_repo = PvtStatusRepositoryFS()
    cell_infos: List[CellInfo] = []
    
    for cell in out.cells:
        cell_root = None
        if cell.type == "sis" and out.sis_root:
            cell_root = Path(out.sis_root) / cell.cell
        elif cell.type == "nt" and out.nt_root:
            cell_root = Path(out.nt_root) / cell.cell
        
        summary = None
        if cell_root and cell_root.exists():
            try:
                is_nt_cell = (cell.type == "nt")
                summary = status_repo.aggregate_counts(str(cell_root), is_nt=is_nt_cell)
            except Exception:
                summary = None
        
        nt_setup_flag = None
        nt_munge_flag = None
        nt_merge_flag = None
        if cell.type == 'nt' and cell_root:
            try:
                nt_setup_flag = (cell_root / 'pvt_corners.lst').exists()
            except Exception:
                nt_setup_flag = None
            # Determine Munge completion: count .lib files under setupDir/munged_lib and compare to 2 * PVT count
            try:
                munged_dir = cell_root / 'ScratchDir' / 'setupDir' / 'munged_lib'
                logger.info(f"[Munge Status] Cell: {cell.cell}, Checking munged_dir: {munged_dir}")

                lib_counter_uc = CountLibFilesInDirectory()
                lib_count = 0
                if munged_dir.exists() and munged_dir.is_dir():
                    lib_count = lib_counter_uc.execute(str(munged_dir))

                # Read PVT names directly from pvt_corners.lst (ignore comments/blank lines)
                pvt_file = cell_root / 'pvt_corners.lst'
                pvts_len = 0
                pvt_names: List[str] = []
                if pvt_file.exists():
                    try:
                        with pvt_file.open('r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                s = line.strip()
                                if not s or s.startswith('#'):
                                    continue
                                pvt_names.append(s)
                        pvts_len = len(pvt_names)
                    except Exception as e:
                        logger.warning(f"[Munge Status] Cell: {cell.cell}, Error reading pvt_corners.lst: {e}")

                all_no_underscore = bool(pvt_names) and all('_' not in n for n in pvt_names)

                if pvts_len > 0:
                    nt_munge_flag = (lib_count == pvts_len * 2) if lib_count > 0 else False
                    if not nt_munge_flag and all_no_underscore:
                        # Fallback: check raw_lib/<cell> directory when all PVT names lack underscore
                        raw_lib_cell_dir = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'release' / 'raw_lib' / cell.cell
                        try:
                            if raw_lib_cell_dir.exists() and raw_lib_cell_dir.is_dir():
                                raw_lib_count = lib_counter_uc.execute(str(raw_lib_cell_dir))
                                logger.info(f"[Munge Status] Cell: {cell.cell}, raw_lib fallback count={raw_lib_count}, expected={pvts_len * 2}")
                                if raw_lib_count == pvts_len * 2:
                                    nt_munge_flag = True
                        except Exception as e:
                            logger.warning(f"[Munge Status] Cell: {cell.cell}, raw_lib fallback error: {e}")
                else:
                    nt_munge_flag = False
                    logger.warning(f"[Munge Status] Cell: {cell.cell} has 0 PVTs (pvt_corners.lst empty or not found), setting munge to False")
                if nt_munge_flag is False and not (munged_dir.exists() and munged_dir.is_dir()):
                    logger.info(f"[Munge Status] Cell: {cell.cell}, munged_dir does not exist or is not a directory")
            except Exception as e:
                nt_munge_flag = None
                logger.error(f"[Munge Status] Cell: {cell.cell}, Error checking munge status: {e}")

            # Determine Merge completion: count .lib files under release/raw_lib/<cell> using unique merged PVT base names
            try:
                pvt_file = cell_root / 'pvt_corners.lst'
                pvt_mode_list: List[str] = []
                if pvt_file.exists():
                    try:
                        with pvt_file.open('r', encoding='utf-8', errors='ignore') as f:
                            for line in f:
                                s = line.strip()
                                if not s or s.startswith('#'):
                                    continue
                                pvt_mode_list.append(s)
                    except Exception as e:
                        logger.warning(f"[Merge Status] Cell: {cell.cell}, Error reading pvt_corners.lst: {e}")

                merge_uc = MergePVTMode()
                unique_pvts, unique_count = merge_uc.execute(pvt_mode_list) if pvt_mode_list else ([], 0)

                raw_lib_cell_dir = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'release' / 'raw_lib' / cell.cell
                if unique_count > 0 and raw_lib_cell_dir.exists() and raw_lib_cell_dir.is_dir():
                    try:
                        lib_counter_uc = CountLibFilesInDirectory()
                        raw_lib_count = lib_counter_uc.execute(str(raw_lib_cell_dir))
                        expected = unique_count * 2
                        nt_merge_flag = (raw_lib_count == expected)
                        logger.info(f"[Merge Status] Cell: {cell.cell}, raw_lib_count={raw_lib_count}, expected={expected}, complete={nt_merge_flag}")
                    except Exception as e:
                        nt_merge_flag = None
                        logger.error(f"[Merge Status] Cell: {cell.cell}, Error counting raw_lib files: {e}")
                else:
                    nt_merge_flag = False if unique_count > 0 else False
                    if unique_count == 0:
                        logger.info(f"[Merge Status] Cell: {cell.cell}, no PVT modes found for merge (unique_count=0)")
                    elif not raw_lib_cell_dir.exists():
                        logger.info(f"[Merge Status] Cell: {cell.cell}, raw_lib directory missing: {raw_lib_cell_dir}")
            except Exception as e:
                nt_merge_flag = None
                logger.error(f"[Merge Status] Cell: {cell.cell}, Unexpected error: {e}")
        
        # Check if TMQA report exists in QA path (replaces brief.sum view)
        brief_sum_exists = None
        try:
            report_path = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'quality' / '3_qa' / cell.cell / f"{cell.cell}_TMQA_Report.xlsx"
            brief_sum_exists = report_path.exists()
        except Exception:
            brief_sum_exists = None
        
        cell_infos.append(CellInfo(
            cell=cell.cell,
            type=cell.type,
            pvts=cell.pvts,
            pvt_count=cell.pvt_count,
            netlist_version=cell.netlist_version,
            final_libs=cell.final_libs,
            pvt_status_summary=summary,
            nt_setup_complete=nt_setup_flag if cell.type == 'nt' else None,
            nt_munge_complete=nt_munge_flag if cell.type == 'nt' else None,
            nt_merge_complete=nt_merge_flag if cell.type == 'nt' else None,
            brief_sum_exists=brief_sum_exists,
        ))
    
    resp = {
        "project": project,
        "subproject": subproject,
        "cells": cell_infos,
    }
    
    if debug:
        resp.update({
            "resolved_sis_path": out.sis_root,
            "resolved_nt_path": out.nt_root,
            "sis_candidates": out.sis_candidates,
            "nt_candidates": out.nt_candidates,
            "note": out.note,
        })
    
    return CellList(**resp)

@router.post("/{project}/{subproject}/{cell}/sync-inst", response_model=SyncInstStatusDTO)
async def sync_inst(project: str, subproject: str, cell: str, cell_type: str = Query("sis"), uc: SyncInstFile = Depends(get_sync_inst_file_uc)):
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    if cell_type not in ("sis", "nt"):
        raise HTTPException(status_code=400, detail="Invalid cell_type")
    out = uc.execute(SyncInstFileInput(project=project, subproject=subproject, cell=cell, cell_type=cell_type))
    return SyncInstStatusDTO(project=project, subproject=subproject, cell=cell, cell_type=cell_type, synced=out.synced, note=out.note, error=out.error)

@router.get("/{project}/{subproject}/cells/{cell}/brief-sum")
async def read_brief_sum(project: str, subproject: str, cell: str):
    """Read brief.sum file from QA directory."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    try:
        brief_sum_path = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'quality' / '3_qa' / cell / 'brief.sum'
        
        if not brief_sum_path.exists():
            raise HTTPException(status_code=404, detail="brief.sum file not found")
        
        content = brief_sum_path.read_text(encoding='utf-8', errors='replace')
        return {
            "project": project,
            "subproject": subproject,
            "cell": cell,
            "content": content,
            "path": str(brief_sum_path)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading brief.sum: {str(e)}")


@router.get("/{project}/{subproject}/diagnose", response_model=DiagnoseResult)
async def diagnose_saf(
    project: str,
    subproject: str,
    uc: DiagnoseSaf = Depends(get_diagnose_saf_uc)
):
    """Diagnostic endpoint for SAF path resolution (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject")):
        _validate_component(v, f)
    
    out = uc.execute(DiagnoseSafInput(project=project, subproject=subproject))
    
    from app.infrastructure.fs.project_root import PROJECTS_BASE
    
    return DiagnoseResult(
        project=project,
        subproject=subproject,
        base_dir=str(PROJECTS_BASE),
        sis_root=out.sis_root,
        candidate_paths=out.candidate_paths,
        sis_root_exists=out.sis_root_exists,
        sample_entries=out.sample_entries,
        char_dirs_found=out.char_dirs_found,
        first_char_dirs=out.first_char_dirs,
    )

@router.get("/{project}/{subproject}/cells/{cell}/taskqueue", response_model=TaskQueueStatus)
async def get_task_queue_status(
    project: str,
    subproject: str,
    cell: str,
    cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'"),
    uc: GetTaskQueueStatus = Depends(get_task_queue_status_uc)
):
    """Get task queue status for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    # Note: Task queue is only supported for SiS cells currently
    # If NT support is needed, update GetTaskQueueStatus use case to handle both types
    if cell_type != "sis":
        raise HTTPException(status_code=400, detail="Task queue is only supported for SiS cells")
    
    try:
        out = uc.execute(GetTaskQueueStatusInput(project=project, subproject=subproject, cell=cell))
        
        # Convert back to TaskQueueStatus schema
        return TaskQueueStatus(
            project=out.project,
            subproject=out.subproject,
            cell=out.cell,
            exists_task_queue=out.exists_task_queue,
            exists_monte_carlo=out.exists_monte_carlo,
            values=TaskQueueRequest(**out.values),
            simulator=out.simulator,
            sis_task_queue_path=out.sis_task_queue_path,
            monte_carlo_settings_path=out.monte_carlo_settings_path,
            note=out.note,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{project}/{subproject}/cells/{cell}/taskqueue", response_model=TaskQueueResult)
async def create_task_queue_files(
    project: str,
    subproject: str,
    cell: str,
    req: TaskQueueRequest = Body(...),
    uc: WriteTaskQueue = Depends(write_task_queue_uc)
):
    """Create task queue configuration files for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    try:
        out = uc.execute(WriteTaskQueueInput(project=project, subproject=subproject, cell=cell, request=req.model_dump()))
        
        # Convert to TaskQueueResult schema
        return TaskQueueResult(
            project=out.project,
            subproject=out.subproject,
            cell=out.cell,
            sis_task_queue_path=out.sis_task_queue_path,
            bytes_written_task_queue=out.bytes_written_task_queue,
            monte_carlo_settings_path=out.monte_carlo_settings_path,
            bytes_written_montecarlo=out.bytes_written_montecarlo,
            simulator=out.simulator,
            note=out.note,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/{project}/{subproject}/cells/{cell}/postedit-lib-count", response_model=PosteditLibCountResult)
async def get_postedit_lib_count(
    project: str,
    subproject: str,
    cell: str,
    postedit_libs_path: Optional[str] = Query(None, description="Custom Postedit_libs path (overrides default)"),
    pvt_count: int = Query(8, description="Number of PVT corners for this cell"),
    uc: CountPosteditLibs = Depends(get_count_postedit_libs_uc)
):
    """Count libs in postedit directory for a SAF cell (Clean Architecture endpoint).
    
    The button will be green when lib_count >= (2 * pvt_count), indicating completion.
    By default, expects 2 libs per PVT corner (pvt_count defaults to 8, so 16 libs total).
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    out = uc.execute(CountPosteditLibsInput(
        project=project,
        subproject=subproject,
        cell=cell,
        postedit_libs_path=postedit_libs_path,
        pvt_count=pvt_count
    ))
    return PosteditLibCountResult(
        project=out.project,
        subproject=out.subproject,
        cell=out.cell,
        path=out.path,
        lib_count=out.lib_count,
        note=out.note
    )

@router.get("/{project}/{subproject}/cells/{cell}/postqa-lib-count", response_model=PostQALibCountResult)
async def get_postqa_lib_count(
    project: str,
    subproject: str,
    cell: str,
    pvt_count: int = Query(8, description="Number of PVT corners (expected libs = 2 * pvt_count)"),
    uc: CountPostqaLibs = Depends(get_count_postqa_libs_uc)
):
    """Count libs in PostQA directory for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    out = uc.execute(CountPostqaLibsInput(project=project, subproject=subproject, cell=cell, pvt_count=pvt_count))
    return PostQALibCountResult(
        project=out.project,
        subproject=out.subproject,
        cell=out.cell,
        path=out.path,
        lib_count=out.lib_count,
        expected_count=out.expected_count,
        note=out.note
    )

@router.get("/{project}/{subproject}/cells/{cell}/netlist-debug")
async def get_netlist_debug(
    project: str,
    subproject: str,
    cell: str,
    cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'"),
    uc: GetNetlistDebug = Depends(get_netlist_debug_uc)
):
    """Debug netlist file presence for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    out = uc.execute(GetNetlistDebugInput(
        project=project,
        subproject=subproject,
        cell=cell,
        cell_type=cell_type
    ))
    
    return {
        "cell": out.cell,
        "cell_type": out.cell_type,
        "netlist_version": out.netlist_version,
        "base_extr_dir": out.base_extr_dir,
        "base_exists": out.base_exists,
        "target_dir": out.target_dir,
        "target_exists": out.target_exists,
        "expected_pattern": out.expected_pattern,
        "spf_files": [f.__dict__ for f in out.spf_files],
        "fallback_search": out.fallback_search,
    }

@router.post("/{project}/{subproject}/cells/{cell}/sync-netlist", response_model=NetlistSyncResult)
async def sync_netlist(
    project: str,
    subproject: str,
    cell: str,
    cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'"),
    uc: SyncNetlist = Depends(get_sync_netlist_uc)
):
    """Sync netlist from Perforce for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    out = uc.execute(SyncNetlistInput(
        project=project,
        subproject=subproject,
        cell=cell,
        cell_type=cell_type
    ))
    
    return NetlistSyncResult(
        project=project,
        subproject=subproject,
        cell=cell,
        cell_type=cell_type,
        depot_path=out.depot_path,
        synced=out.synced,
        return_code=out.return_code,
        stdout=out.stdout,
        stderr=out.stderr,
        note=out.note,
    )

@router.get("/{project}/{subproject}/cells/{cell}/pvt/{pvt}/files", response_model=FileListResponse)
async def list_pvt_files(
    project: str,
    subproject: str,
    cell: str,
    pvt: str,
    path: str = Query('', description="Relative subpath inside PVT root"),
    uc: ListPvtFiles = Depends(get_list_pvt_files_uc)
):
    """List files in a SAF cell PVT directory (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (pvt, "pvt")):
        _validate_component(v, f)
    
    try:
        out = uc.execute(ListPvtFilesInput(
            project=project,
            subproject=subproject,
            cell=cell,
            pvt=pvt,
            path=path
        ))
        return FileListResponse(
            project=out.project,
            subproject=out.subproject,
            cell=out.cell,
            pvt=out.pvt,
            path=out.path,
            entries=out.entries
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project}/{subproject}/cells/{cell}/pvt/{pvt}/file", response_model=FileReadResponse)
async def read_pvt_file(
    project: str,
    subproject: str,
    cell: str,
    pvt: str,
    path: str = Query(..., description="Relative file path inside PVT root"),
    uc: ReadPvtFile = Depends(get_read_pvt_file_uc)
):
    """Read a file from a SAF cell PVT directory (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (pvt, "pvt")):
        _validate_component(v, f)
    
    try:
        out = uc.execute(ReadPvtFileInput(
            project=project,
            subproject=subproject,
            cell=cell,
            pvt=pvt,
            path=path
        ))
        return FileReadResponse(
            project=out.project,
            subproject=out.subproject,
            cell=out.cell,
            pvt=out.pvt,
            path=out.path,
            name=out.name,
            size=out.size,
            is_text=out.is_text,
            truncated=out.truncated,
            content=out.content
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{project}/{subproject}/cells/{cell}/pvt/{pvt}/file", response_model=FileWriteResponse)
async def write_pvt_file(
    project: str,
    subproject: str,
    cell: str,
    pvt: str,
    req: FileWriteRequest,
    uc: WritePvtFile = Depends(get_write_pvt_file_uc)
):
    """Write a file to a SAF cell PVT directory (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (pvt, "pvt")):
        _validate_component(v, f)
    
    try:
        out = uc.execute(WritePvtFileInput(
            project=project,
            subproject=subproject,
            cell=cell,
            pvt=pvt,
            path=req.path,
            content=req.content
        ))
        return FileWriteResponse(
            project=out.project,
            subproject=out.subproject,
            cell=out.cell,
            pvt=out.pvt,
            name=out.name,
            bytes=out.bytes,
            created=out.created,
            note=out.note
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{project}/{subproject}/cells/{cell}/postedit/defaults", response_model=PostEditDefaults)
async def get_postedit_defaults(
    project: str,
    subproject: str,
    cell: str,
    uc: GetPostEditDefaults = Depends(get_postedit_defaults_uc)
):
    """Get default post-edit settings for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    out = uc.execute(GetPostEditDefaultsInput(project=project, subproject=subproject, cell=cell))
    
    # Preserve heuristic plan selection (UI concern, kept in router)
    if 'ucie2phy' in cell:
        plan = '//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx'
    elif 'ucie3phy' in cell:
        plan = '//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/plan/uciephy_constraint.xlsx'
    elif 'uciephy' in cell:
        plan = '//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/plan/uciephy_constraint.xlsx'
    else:
        plan = '//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx'
    
    return PostEditDefaults(
        config_dir=out.config_dir,
        lib_path=out.lib_path,
        reference_path=out.reference_path,
        plan=plan,
        pt='2022.12-SP5',
        reformat='sis',
        copyReference=False,
        reorder=True,
    )

@router.post("/{project}/{subproject}/cells/{cell}/postedit", response_model=PostEditResult)
async def run_postedit(
    project: str,
    subproject: str,
    cell: str,
    req: PostEditRequest = Body(...),
    uc: RunPostEdit = Depends(get_run_postedit_uc)
):
    """Run post-edit process for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
    quality_dir = BASE_DIR / project / subproject / "design" / "timing" / "quality" / "1_postedit"
    
    cmd_parts = [
        "TimingCloseBeta.py", "-postedit", "-cell", req.cell, "-configfile", req.configfile,
        "-lib", req.lib, "-plan", req.plan, "-pt", req.pt
    ]
    if req.reformat:
        cmd_parts.extend(["-reformat", req.reformat])
    if req.copyReference and req.reference:
        cmd_parts.extend(["-reference", req.reference])
    if req.reorder:
        cmd_parts.append("-reorder")
    
    try:
        out = uc.execute(RunPostEditInput(
            project=project,
            subproject=subproject,
            cell=req.cell,
            configfile=req.configfile,
            lib=req.lib,
            plan=req.plan,
            reference=req.reference,
            copy_reference=req.copyReference,
            reformat=req.reformat,
            reorder=req.reorder,
            leakage=False,
            pt=req.pt,
            output=None,
        ))
        
        return PostEditResult(
            cell=req.cell,
            project=project,
            subproject=subproject,
            started=out.started,
            cmd=" ".join(cmd_parts),
            note=out.note,
            working_dir=str(quality_dir),
            configfile_path=req.configfile,
            return_code=out.return_code,
            stdout=out.stdout,
            stderr=out.stderr,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail={
            "error": str(e),
            "working_dir": str(quality_dir),
            "configfile_path": req.configfile,
            "cmd": " ".join(cmd_parts)
        })
    except ValueError as e:
        raise HTTPException(status_code=400, detail={
            "error": str(e),
            "working_dir": str(quality_dir),
            "configfile_path": req.configfile,
            "cmd": " ".join(cmd_parts)
        })
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "working_dir": str(quality_dir),
            "configfile_path": req.configfile,
            "cmd": " ".join(cmd_parts)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            "error": f"Unexpected error: {e}",
            "working_dir": str(quality_dir),
            "configfile_path": req.configfile,
            "cmd": " ".join(cmd_parts)
        })

@router.post("/{project}/{subproject}/cells/{cell}/job", response_model=JobResult)
async def create_job_script(
    project: str,
    subproject: str,
    cell: str,
    cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'"),
    req: Optional[JobRequest] = Body(None, description="Job parameters (omit when run-only or for NT cells)."),
    run: bool = Query(False, description="Execute runall.csh after (or without) writing and capture output"),
    run_timeout: int = Query(300, description="Timeout in seconds for runall.csh execution"),
    prep_uc: PrepareAndRunJob = Depends(prepare_and_run_job_uc),
):
    """Generate and optionally run job script for a SAF cell (Clean Architecture endpoint)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
    
    # Determine cell root based on type
    if cell_type == "nt":
        cell_root_path = BASE_DIR / project / subproject / "design" / "timing" / "nt"
    else:
        cell_root_path = BASE_DIR / project / subproject / "design" / "timing" / "sis"
    
    # Create directory if needed
    try:
        cell_root_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create directory: {e}")
    
    cell_dir = cell_root_path / cell
    if not cell_dir.exists():
        try:
            cell_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create cell directory {cell_dir}: {e}")
    
    try:
        prep_out = prep_uc.execute(PrepareAndRunJobInput(
            project=project,
            subproject=subproject,
            cell=cell,
            cell_type=cell_type,
            generate=req is not None,
            hspice_version=req.hspiceVersion if req else None,
            finesim_version=req.finesimVersion if req else None,
            primesim_version=req.primesimVersion if req else None,
            siliconsmart_version=req.siliconsmartVersion if req else None,
            queue=req.queue if req else None,
            netlist_type=req.netlistType if req else None,
            pvt_list=req.pvt_list if req else None,
            selected_pvts=req.selected_pvts if req else None,
            raw_lib_paths=req.raw_lib_paths if req else None,
            nt_option=req.nt_option if req else None,
            bsub_args=req.bsub_args if req else None,
            # Pass through optional bsub args for NT script generation
            internal_saf=req.internal_saf if req else False,
            run=run,
            timeout=run_timeout,
        ))
        
        note = prep_out.note
        if req and cell_type == 'nt' and req.selected_pvts:
            note = (note or '') + f" (NT --sim \"{' '.join(req.selected_pvts)}\")"
        elif req and cell_type == 'nt' and req.nt_option:
            note = (note or '') + f" (NT option: {req.nt_option})"
        
        return JobResult(
            project=project,
            subproject=subproject,
            cell=cell,
            script_path=str(prep_out.script_path),
            bytes_written=prep_out.bytes_written,
            note=note,
            working_dir=str(prep_out.script_path.parent),
            exec_cmd=prep_out.exec_cmd,
            ran=prep_out.ran,
            return_code=prep_out.return_code,
            stdout=prep_out.stdout,
            stderr=prep_out.stderr,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {e}")


@router.websocket("/{project}/{subproject}/cells/{cell}/execute/ws")
async def execute_job_script_ws(
    websocket: WebSocket,
    project: str,
    subproject: str,
    cell: str,
    cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'")
):
    """Execute runall.csh with real-time WebSocket streaming (using reusable infrastructure)."""
    await websocket.accept()
    
    try:
        # Validate inputs
        for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
            _validate_component(v, f)
        
        from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
        
        # Determine cell root based on type
        if cell_type == "nt":
            cell_root_path = BASE_DIR / project / subproject / "design" / "timing" / "nt"
        else:
            cell_root_path = BASE_DIR / project / subproject / "design" / "timing" / "sis"
        
        cell_dir = cell_root_path / cell
        
        # Create cell directory if needed
        if not cell_dir.exists():
            try:
                cell_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                await websocket.send_json({"event": "error", "detail": f"Failed to create cell directory: {e}"})
                await websocket.close()
                return
        
        # Script is in the parent directory (sis/ or nt/), not in the cell directory
        script_path = cell_root_path / "runall.csh"
        if not script_path.exists():
            await websocket.send_json({"event": "error", "detail": "runall.csh not found. Generate script first via Settings dialog."})
            await websocket.close()
            return
        
        # Prepare setup messages
        setup_messages = [
            f"[Setup] Cell: {cell} (type: {cell_type})\n",
            f"[Setup] Script: {script_path}\n",
            f"[Setup] Working directory: {cell_root_path}\n"
        ]
        
        # Use reusable WebSocketStreamExecutor
        executor = WebSocketStreamExecutor(websocket)
        result = await executor.execute_script(
            script_path=script_path,
            working_dir=cell_root_path,
            shell="/bin/csh",
            setup_messages=setup_messages
        )
        
        # WebSocket automatically closed by executor
        try:
            await websocket.close()
        except Exception:
            pass
            
    except Exception as e:
        try:
            await websocket.send_json({"event": "error", "detail": f"Unexpected error: {e}"})
            await websocket.close()
        except Exception:
            pass


__all__ = ["router"]


