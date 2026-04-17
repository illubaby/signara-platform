"""QA HTTP schemas - Pydantic models for API requests/responses."""
from pydantic import BaseModel, Field
from typing import List, Optional


class QACellSchema(BaseModel):
    cell: str
    has_plan: bool = False
    has_summary: bool = False
    last_run: Optional[str] = None
    summary_rows: int = 0


class QACellListSchema(BaseModel):
    project: str
    subproject: str
    cells: List[QACellSchema]
    note: Optional[str] = None


class QADefaultsSchema(BaseModel):
    project: str
    subproject: str
    cell: Optional[str] = None
    plan_file: Optional[str] = None
    pt_version: str = "2022.12-SP5"
    summary_path: Optional[str] = None
    cell_list_file: Optional[str] = None
    header_file: Optional[str] = None
    data_release: Optional[str] = None
    outdir: Optional[str] = None
    queue: Optional[str] = None
    run_dir: Optional[str] = None
    note: Optional[str] = None


class QAChecksSchema(BaseModel):
    checks: List[str]


class AvailableCellsSchema(BaseModel):
    cells: List[str]
    note: Optional[str] = None


class RunQARequestSchema(BaseModel):
    selected_cells: List[str] = Field(..., description="List of selected cell names")
    data_release: str = Field(..., description="Data Release (aLibs) path")
    header_file: str = Field(..., description="Header file path")
    cell_list_file: Optional[str] = Field(None, description="Optional path to existing cell list file (dwc_cells.lst)")
    project: str = Field(..., description="Project name (prj)")
    release: str = Field(..., description="Release tag (rel)")
    plan_file: Optional[str] = Field(None, description="QA plan file path")
    outdir: str = Field(..., description="Output directory")
    queue: str = Field("normal", description="Queue name (-qsub)")
    run_dir: Optional[str] = Field(None, description="Directory where the script will be executed")
    selected_checks: List[str] = Field(default_factory=list, description="List of optional QA checks to enable")


class RunQAResultSchema(BaseModel):
    project: str
    subproject: str
    job_id: str
    cmd: str
    started: bool
    working_dir: Optional[str]
    script_path: Optional[str]
    effective_checks: List[str]
    warnings: List[str]
    note: Optional[str] = None


class QASummaryRowSchema(BaseModel):
    test: str
    status: str
    value: Optional[str] = None
    detail: Optional[str] = None


class QASummarySchema(BaseModel):
    project: str
    subproject: str
    cell: str
    rows: List[QASummaryRowSchema]
    source: Optional[str]
    note: Optional[str] = None


class QAJobStatusSchema(BaseModel):
    job_id: str
    status: str
    stdout: str
    stderr: str
    pid: Optional[int]
    script_path: Optional[str]
    command: str


class CellCheckMatrixSchema(BaseModel):
    project: str
    subproject: str
    run_dir: str
    cell_names: List[str] = Field(..., description="Column headers: cell names")
    check_items: List[str] = Field(..., description="Row headers: check item names")
    status_matrix: List[List[str]] = Field(..., description="Matrix[check_index][cell_index] = status")
    cells_with_brief_sum: List[str] = Field(..., description="Cells that have brief.sum files")
    missing_cells: List[str] = Field(..., description="Cells without brief.sum files")
    note: Optional[str] = None
