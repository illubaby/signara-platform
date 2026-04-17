"""Domain entities for Timing QC feature.

These dataclasses represent pure business data with no external side-effects.
They were migrated from legacy qc_service.py as part of Phase 0 scaffold.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class QCCellMeta:
    cell: str
    has_qcplan: bool
    has_netlist: bool
    has_data: bool
    has_common_source: bool
    has_ref: bool
    delay_rows: int
    constraint_rows: int

@dataclass(frozen=True)
class QCDefaultPaths:
    qcplan_path: Optional[str]
    netlist_path: Optional[str]
    data_path: Optional[str]
    datastore_paths: Optional[List[str]]
    common_source_path: Optional[str]
    timing_paths_path: Optional[str]
    ref_data_path: Optional[str]
    update: bool
    adjustment: bool
    no_wf: bool
    xtalk_rel_net: bool
    hierarchy: Optional[str]
    verbose: Optional[str]
    include: Optional[str]
    xtalk: Optional[str]
    primesim: Optional[str]
    hspice: Optional[str]
    index: Optional[str]
    phase: Optional[str]
    debug_path: Optional[str]
    tmqc_internal_node_map_path: Optional[str]
    note: Optional[str]

@dataclass(frozen=True)
class PVTRowMeta:
    pvt: str
    status: str  # Passed / Fail / In Progress / Not Started
    log_type: Optional[str]
    log_path: Optional[str]
    pocv_file_status: Optional[str]
    note: Optional[str]

@dataclass(frozen=True)
class TableRowData:
    testbench: str
    pvt: str
    status: str
    slack: Optional[float] = None
    factorx: Optional[float] = None
    program_time: Optional[str] = None
    path: Optional[str] = None
    log_file: Optional[str] = None
    notes: Optional[str] = None

__all__ = [
    "QCCellMeta",
    "QCDefaultPaths",
    "PVTRowMeta",
    "TableRowData",
]