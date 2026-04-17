"""QA domain entities - pure business objects."""
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=True)
class QACell:
    """Represents a QA cell with its metadata."""
    cell: str
    has_plan: bool = False
    has_summary: bool = False
    last_run: Optional[str] = None
    summary_rows: int = 0


@dataclass(frozen=True)
class QASummaryRow:
    """Individual test result in QA summary."""
    test: str
    status: str
    value: Optional[str] = None
    detail: Optional[str] = None


@dataclass(frozen=True)
class QASummary:
    """Complete QA summary for a cell."""
    project: str
    subproject: str
    cell: str
    rows: List[QASummaryRow]
    source: Optional[str] = None


@dataclass(frozen=True)
class QADefaults:
    """Default parameters for QA execution."""
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


@dataclass(frozen=True)
class QARunRequest:
    """Request to run QA checks."""
    selected_cells: List[str]
    data_release: str
    header_file: str
    cell_list_file: Optional[str]
    project: str
    release: str
    plan_file: Optional[str]
    outdir: str
    queue: str
    run_dir: Optional[str]
    selected_checks: List[str]


@dataclass(frozen=True)
class QARunResult:
    """Result of QA execution."""
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


@dataclass(frozen=True)
class QAJobStatus:
    """Status of a running QA job."""
    job_id: str
    status: str
    stdout: str
    stderr: str
    pid: Optional[int]
    script_path: Optional[str]
    command: str


@dataclass(frozen=True)
class BriefSumItem:
    """Single check item from brief.sum file."""
    check_name: str
    status: str


@dataclass(frozen=True)
class CellCheckMatrix:
    """Matrix view of QA checks: rows=check items, columns=cells."""
    project: str
    subproject: str
    run_dir: str
    cell_names: List[str]
    check_items: List[str]
    status_matrix: List[List[str]]  # [check_index][cell_index] = status
    cells_with_brief_sum: List[str]  # Cells that have brief.sum files
    missing_cells: List[str]  # Cells without brief.sum files
