from typing import Optional, List
from pydantic import BaseModel

# Pydantic schemas extracted from legacy router (post_edit.py) to align with architecture.
# Router now imports these models instead of defining them inline.

class ConfigSaveRequest(BaseModel):
    path: str
    content: str

class ConfigSaveResult(BaseModel):
    path: str
    bytes_written: int
    note: str

class RunPostEditRequest(BaseModel):
    cell: str
    configfile: str
    lib: str
    reference: Optional[str] = None
    copyReference: bool = False
    plan: str
    reformat: Optional[str] = None  # pt | sis (optional)
    reorder: bool = False
    leakage: bool = False
    pt: str
    output: Optional[str] = None

class RunPostEditResult(BaseModel):
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

class PostEditCell(BaseModel):
    cell: str
    config_path: str
    exists: bool

class PostEditCellList(BaseModel):
    project: str
    subproject: str
    base_dir: str
    config_dir: str
    cells: List[PostEditCell]
    note: Optional[str] = None

class PostEditDefaults(BaseModel):
    project: str
    subproject: str
    cell: Optional[str]
    base_dir: str
    config_dir: str
    config_file: Optional[str]
    lib_path: str
    reference_path: str
    output_path: str
    note: Optional[str] = None

class CellMetric(BaseModel):
    cell: str
    aLibs_count: int
    updated_libs_count: int
    complete: bool

class PostEditMetrics(BaseModel):
    project: str
    subproject: str
    cells: List[CellMetric]

__all__ = [
    "ConfigSaveRequest", "ConfigSaveResult", "RunPostEditRequest", "RunPostEditResult",
    "PostEditCell", "PostEditCellList", "PostEditDefaults", "CellMetric", "PostEditMetrics"
]
