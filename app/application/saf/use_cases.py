"""Application use-cases for SAF (Phase 2 additions).

Existing: GetPvtStatuses.
Added: ListSafCells, SyncInstFile (thin orchestration over repositories).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.domain.saf.repositories import PvtStatusRepository, SafCellRepository, SafPerforceRepository
from app.domain.saf.entities import Cell

@dataclass
class GetPvtStatusesInput:
    cell_dir: str
    is_nt: bool = False

@dataclass
class GetPvtStatusesOutput:
    statuses: Dict[str, str]
    summary: Dict[str, int]

class GetPvtStatuses:
    def __init__(self, repo: PvtStatusRepository) -> None:
        self.repo = repo

    def execute(self, inp: GetPvtStatusesInput) -> GetPvtStatusesOutput:
        statuses = self.repo.statuses_for_cell(inp.cell_dir, is_nt=inp.is_nt)
        summary = self.repo.aggregate_counts(inp.cell_dir, is_nt=inp.is_nt)
        return GetPvtStatusesOutput(statuses=statuses, summary=summary)

__all__ = ["GetPvtStatuses", "GetPvtStatusesInput", "GetPvtStatusesOutput"]


# ---- Phase 2: New SAF cell & sync use-cases ----

@dataclass
class ListSafCellsInput:
    project: str
    subproject: str
    cell_type: str = "sis"
    force_refresh: bool = False  # reserved for caching strategy

@dataclass
class ListSafCellsOutput:
    cells: List[Cell]
    sis_root: Optional[str]
    nt_root: Optional[str]
    note: Optional[str] = None

class ListSafCells:
    def __init__(self, fs_repo: SafCellRepository) -> None:
        self.fs_repo = fs_repo

    def execute(self, inp: ListSafCellsInput) -> ListSafCellsOutput:
        sis_root = self.fs_repo.resolve_sis_root(inp.project, inp.subproject)
        nt_root = self.fs_repo.resolve_nt_root(inp.project, inp.subproject)
        cells = self.fs_repo.list_local_cells(inp.project, inp.subproject, inp.cell_type)
        return ListSafCellsOutput(cells=cells, sis_root=sis_root, nt_root=nt_root, note=None)

@dataclass
class SyncInstFileInput:
    project: str
    subproject: str
    cell: str
    cell_type: str = "sis"

@dataclass
class SyncInstFileOutput:
    synced: bool
    note: str
    error: Optional[str] = None

class SyncInstFile:
    def __init__(self, p4_repo: SafPerforceRepository) -> None:
        self.p4_repo = p4_repo

    def execute(self, inp: SyncInstFileInput) -> SyncInstFileOutput:
        meta = self.p4_repo.sync_inst_file(inp.project, inp.subproject, inp.cell, inp.cell_type)
        return SyncInstFileOutput(synced=bool(meta.get("synced")), note=str(meta.get("note", "")), error=meta.get("error"))

__all__ += [
    "ListSafCells", "ListSafCellsInput", "ListSafCellsOutput",
    "SyncInstFile", "SyncInstFileInput", "SyncInstFileOutput",
]
