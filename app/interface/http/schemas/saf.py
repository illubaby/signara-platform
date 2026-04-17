"""Pydantic schemas for SAF endpoints (Phase 4 extraction)."""
from __future__ import annotations
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.interface.http.schemas.task_queue import (
    TaskQueueStatusSchema as TaskQueueStatus,
    TaskQueueRequestSchema as TaskQueueRequest,
    TaskQueueResultSchema as TaskQueueResult
)

class CellInfo(BaseModel):
    cell: str
    type: str
    pvts: List[str]
    pvt_count: int
    netlist_version: str
    final_libs: int
    pvt_status_summary: Optional[Dict[str, int]] = None
    nt_setup_complete: Optional[bool] = None
    # New: NT Munge completion flag – True when munged_lib contains 2x .lib files vs PVT count
    nt_munge_complete: Optional[bool] = None
    # New: NT Merge completion flag – True when raw_lib/<cell> has 2x .lib files vs unique (mode-merged) PVT count
    nt_merge_complete: Optional[bool] = None
    brief_sum_exists: Optional[bool] = None

class CellList(BaseModel):
    project: str
    subproject: str
    cells: List[CellInfo]
    resolved_sis_path: Optional[str] = None
    resolved_nt_path: Optional[str] = None
    sis_candidates: Optional[List[str]] = None
    nt_candidates: Optional[List[str]] = None
    resolved_path: Optional[str] = None  # deprecated, kept for compatibility
    candidate_paths: Optional[List[str]] = None  # deprecated, kept for compatibility
    note: Optional[str] = None

class DiagnoseResult(BaseModel):
    project: str
    subproject: str
    base_dir: str
    sis_root: Optional[str]
    candidate_paths: List[str]
    sis_root_exists: bool
    sample_entries: List[str]
    char_dirs_found: int
    first_char_dirs: List[str]

class JobRequest(BaseModel):
    hspiceVersion: str = "2023.12-1"
    finesimVersion: str = "2023.12-1"
    primesimVersion: Optional[str] = "2023.12-1"
    siliconsmartVersion: str = "2024.09-SP4"
    queue: str = "normal"
    netlistType: str = "lpe"
    pvt_list: Optional[str] = None
    selected_pvts: Optional[List[str]] = None
    raw_lib_paths: Optional[str] = None
    nt_option: Optional[str] = "--merge"
    internal_saf: bool = False
    # Optional bsub args to pass into NT run script. UI default/placeholder expected.
    bsub_args: Optional[str] = "-app quick -n 1 -M 50G -R 'span[hosts=1] rusage[mem=5GB,scratch_free=5]'"

class JobResult(BaseModel):
    project: str
    subproject: str
    cell: str
    script_path: str
    bytes_written: int
    note: Optional[str] = None
    working_dir: Optional[str] = None
    exec_cmd: Optional[str] = None
    ran: bool = False
    return_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None

class FileListResponse(BaseModel):
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str
    entries: List[Dict]

class FileReadResponse(BaseModel):
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str
    name: str
    size: int
    is_text: bool
    truncated: bool
    content: Optional[str] = None

class FileWriteRequest(BaseModel):
    path: str
    content: str

class FileWriteResponse(BaseModel):
    project: str
    subproject: str
    cell: str
    pvt: str
    name: str
    bytes: int
    created: bool
    note: Optional[str] = None

class PVTStatusResponse(BaseModel):
    project: str
    subproject: str
    cell: str
    statuses: Dict[str, str]
    summary: Dict[str, int]

class PVTListResponse(BaseModel):
    project: str
    subproject: str
    pvts: List[str]
    note: Optional[str] = None

class PostEditDefaults(BaseModel):
    config_dir: str
    lib_path: str
    reference_path: str
    plan: str
    pt: str
    reformat: str
    copyReference: bool
    reorder: bool

class PostEditRequest(BaseModel):
    cell: str
    configfile: str
    lib: str
    reference: Optional[str] = None
    copyReference: bool = False
    plan: str
    reformat: Optional[str] = None
    reorder: bool = False
    pt: str

class PostEditResult(BaseModel):
    cell: str
    project: str
    subproject: str
    started: bool
    cmd: str
    note: Optional[str] = None
    working_dir: str
    configfile_path: str
    return_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None

class NetlistSyncResult(BaseModel):
    project: str
    subproject: str
    cell: str
    cell_type: str
    depot_path: str
    synced: bool
    return_code: int
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    note: Optional[str] = None

class PosteditLibCountResult(BaseModel):
    project: str
    subproject: str
    cell: str
    path: str
    lib_count: int
    note: Optional[str] = None

class PostQALibCountResult(BaseModel):
    project: str
    subproject: str
    cell: str
    path: str
    lib_count: int
    expected_count: int  # 2 * pvt_count
    note: Optional[str] = None

# ----- Legacy DTOs kept for compatibility with saf_router & existing tests -----

class CellDTO(BaseModel):
    cell: str
    type: str
    pvts: List[str]
    pvt_count: int
    netlist_version: str
    final_libs: int

class CellListDTO(BaseModel):
    project: str
    subproject: str
    cell_type: str
    cells: List[CellDTO]
    sis_root: Optional[str] = None
    nt_root: Optional[str] = None
    note: Optional[str] = None

class SyncInstStatusDTO(BaseModel):
    project: str
    subproject: str
    cell: str
    cell_type: str
    synced: bool
    note: Optional[str] = None
    error: Optional[str] = None

# Re-export task queue models from service layer
__all__ = [name for name in list(globals()) if name.endswith('Response') or name.endswith('Result') or name.endswith('Defaults') or name in ('CellInfo','CellList','DiagnoseResult','JobRequest','JobResult','FileWriteRequest','PostEditRequest','CellDTO','CellListDTO','SyncInstStatusDTO','TaskQueueStatus','TaskQueueRequest','TaskQueueResult')]
