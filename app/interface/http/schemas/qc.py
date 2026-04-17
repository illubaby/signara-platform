"""QC Interface Schemas - Pydantic models for Timing QC API.

This module contains all request/response models for the QC feature.
Schemas are separate from domain entities to maintain clean architecture boundaries.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


# ============================================================================
# Cell Listing Schemas (Phase 1)
# ============================================================================

class QCCell(BaseModel):
    """QC cell metadata for listing."""
    cell: str
    has_qcplan: bool = False
    has_netlist: bool = False
    has_data: bool = False
    has_common_source: bool = False
    has_ref: bool = False
    delay_rows: int = 0
    constraint_rows: int = 0
    tmqc_report_exists: Optional[bool] = None


class QCCellList(BaseModel):
    """Response model for cell listing."""
    project: str
    subproject: str
    cells: List[QCCell]
    note: Optional[str] = None


# ============================================================================
# Defaults Schemas (Phase 2)
# ============================================================================

class QCDefaults(BaseModel):
    """Default paths and options for QC cell."""
    project: str
    subproject: str
    cell: str
    qcplan_path: Optional[str] = None
    netlist_path: Optional[str] = None
    data_path: Optional[str] = None
    datastore_paths: Optional[List[str]] = None
    common_source_path: Optional[str] = None
    timing_paths_path: Optional[str] = None
    ref_data_path: Optional[str] = None
    # Additional fields from runall.csh
    update: bool = False
    adjustment: bool = False
    no_wf: bool = False
    xtalk_rel_net: bool = False
    hierarchy: Optional[str] = None
    verbose: Optional[str] = None
    include: Optional[str] = None
    xtalk: Optional[str] = None
    primesim: Optional[str] = None
    hspice: Optional[str] = None
    index: Optional[str] = None
    phase: Optional[str] = None
    debug_path: Optional[str] = None
    tmqc_internal_node_map_path: Optional[str] = None
    note: Optional[str] = None


# ============================================================================
# Testbench Schemas (Phase 3)
# ============================================================================

class TestbenchList(BaseModel):
    """Response model for testbench listing."""
    project: str
    subproject: str
    cell: str
    testbenches: List[str]
    note: Optional[str] = None


class ImportantArcs(BaseModel):
    """Response model for important arc numbers."""
    project: str
    subproject: str
    cell: str
    important_numbers: List[int]
    note: Optional[str] = None


# ============================================================================
# Status Schemas (Phase 4)
# ============================================================================

class PVTRow(BaseModel):
    """PVT-specific execution status."""
    pvt: str
    status: str  # Passed / Fail / In Progress / Not Started
    log_type: Optional[str] = None  # siliconsmart or primelib
    log_path: Optional[str] = None
    pocv_file_status: Optional[str] = None  # Missing / Empty / Exist - status of get_pocv_pbsa_xtalk.txt
    note: Optional[str] = None


class TestbenchStatus(BaseModel):
    """Testbench status with PVT breakdown."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvts: List[PVTRow]
    status: str  # Aggregated: Passed / Fail / In Progress / Not Started
    note: Optional[str] = None


# ============================================================================
# Generate Schemas (Phase 5)
# ============================================================================

class GenerateRequest(BaseModel):
    """Request model for QC table generation."""
    cell: str = Field(..., description="Cell name")
    qcplan: Optional[str] = None
    netlist: Optional[str] = None
    data: Optional[str] = None
    datastore: Optional[List[str]] = None
    common_source: Optional[str] = None
    timing_paths: Optional[str] = None
    ref_data: Optional[str] = None
    update: bool = False  # controls -update -tmqc line
    adjustment: bool = False  # if true add -adjustment
    no_wf: bool = True  # default tick like Adjust -> adds -noWF
    xtalk_rel_net: bool = False  # new simplified xtalk option => -xtalkRelNet
    # Value options (now strings instead of booleans)
    hierarchy: Optional[str] = None  # -hierarchy <value>
    verbose: Optional[str] = None    # -verbose <value>
    include: Optional[str] = None    # -include <dir>
    xtalk: Optional[str] = None      # -xtalk <value>
    primesim: Optional[str] = None   # -primesim <version>
    hspice: Optional[str] = None     # -hspice <version>
    # Legacy compatibility fields (older UI may still send these)
    include_file: Optional[str] = None
    primesim_version: Optional[str] = None
    hspice_version: Optional[str] = None
    index: Optional[str] = None
    phase: Optional[str] = None
    debug_path: Optional[str] = None


class TableRow(BaseModel):
    """Single row in QC delay/constraint table."""
    testbench: str
    pvt: str
    status: str
    slack: Optional[float] = None
    factorx: Optional[float] = None
    program_time: Optional[str] = None
    path: Optional[str] = None
    log_file: Optional[str] = None
    notes: Optional[str] = None


class GenerateResult(BaseModel):
    """Response model for QC table generation."""
    project: str
    subproject: str
    cell: str
    delay: List[TableRow]
    constraint: List[TableRow]
    source: Dict[str, Optional[str]]
    applied_filters: Dict[str, Any]
    cached: bool = False
    note: Optional[str] = None
    script_path: Optional[str] = None
    ran_script: bool = False
    testbenches: List[str] = []


# ============================================================================
# Script Execution & Task Queue Schemas
# ============================================================================

class RunScriptResult(BaseModel):
    """Response model for script execution."""
    project: str
    subproject: str
    cell: str
    script_path: str
    started: bool
    cmd: str
    working_dir: str
    note: Optional[str] = None


class RunRowRequest(BaseModel):
    """Request model for running a single table row."""
    cell: str
    testbench: str
    pvt: str
    mode: str = "delay"  # or constraint


class RunRowResult(BaseModel):
    """Response model for row execution."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvt: str
    mode: str
    started: bool
    cmd: Optional[str] = None
    working_dir: Optional[str] = None
    note: Optional[str] = None


class RunPvtsRequest(BaseModel):
    """Request model for running multiple PVTs."""
    testbench: str
    pvts: List[str]
    queue_opts: str = '-app normal -n 1 -M 50G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'
    impostor: Optional[str] = None  # "self", "Impostor1", "Impostor2", or None


class PvtJobResult(BaseModel):
    """Result for a single PVT job."""
    pvt: str
    success: bool
    job_id: Optional[str] = None
    message: Optional[str] = None
    command: Optional[str] = None


class RunPvtsResult(BaseModel):
    """Response model for PVT execution."""
    project: str
    subproject: str
    cell: str
    testbench: str
    jobs: List[PvtJobResult]
    note: Optional[str] = None


class LogResult(BaseModel):
    """Response model for log file retrieval."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvt: str
    mode: str
    path: Optional[str]
    exists: bool
    content: Optional[str] = None
    truncated: bool = False


# ============================================================================
# Explorer Schemas
# ============================================================================

class QCFileList(BaseModel):
    """Response model for file listing in QC explorer."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvt: Optional[str]
    path: str
    entries: List[Dict[str, Any]]


class QCFileRead(BaseModel):
    """Response model for file reading in QC explorer."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvt: Optional[str]
    path: str
    name: str
    size: int
    is_text: bool
    truncated: bool
    content: Optional[str] = None


class QCFileWriteRequest(BaseModel):
    """Request model for file writing in QC explorer."""
    path: str
    content: str


class QCFileWriteResponse(BaseModel):
    """Response model for file writing in QC explorer."""
    project: str
    subproject: str
    cell: str
    testbench: str
    pvt: Optional[str]
    name: str
    bytes_written: int
    created: bool
    note: Optional[str] = None


# ============================================================================
# Equalizer Schemas
# ============================================================================

class EqualizerRow(BaseModel):
    """Single row in EqualizeMap.csv."""
    action: str  # EQ, NOEQ
    type: str
    pin: str
    related_pin: str
    when: str
    ff_max_min: str
    tt_max_min: str
    ss_max_min: str
    sf_max_min: str
    status: str  # PASSED, FAILED
    extra_margin: str = "NA"  # Extra margin field


class EqualizerData(BaseModel):
    """Response model for EqualizeMap.csv data."""
    project: str
    subproject: str
    cell: str
    rows: List[EqualizerRow]
    exists: bool
    note: Optional[str] = None


class EqualizerUpdateRequest(BaseModel):
    """Request model for updating EqualizeMap.csv."""
    rows: List[EqualizerRow]


class PostEqualizerRow(BaseModel):
    """Single row in Compatibility_Final.csv."""
    type: str
    pin: str
    related_pin: str
    when: str
    ff_max_min: str
    tt_max_min: str
    ss_max_min: str
    sf_max_min: str
    corner_status: str
    comment: str


class PostEqualizerData(BaseModel):
    """Response model for Compatibility_Final.csv data."""
    project: str
    subproject: str
    cell: str
    rows: List[PostEqualizerRow]
    exists: bool
    note: Optional[str] = None
