"""Application use-cases scaffold for QC feature (Phase 0).

Each use-case will be fleshed out in subsequent phases.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
from app.domain.qc.repositories import (
    QCCellRepository, QCP4VRepository, QCTestbenchRepository,
    QCDefaultsRepository, QCScriptBuilder, QCTablesRepository
)
from app.domain.qc.entities import QCCellMeta, QCDefaultPaths, PVTRowMeta, TableRowData

@dataclass
class ListCells:
    cell_repo: QCCellRepository
    p4v_repo: QCP4VRepository | None = None
    project: str | None = None
    subproject: str | None = None

    def execute(self) -> List[QCCellMeta]:
        if not self.project or not self.subproject:
            return []
        local = self.cell_repo.list_local_cells(self.project, self.subproject)
        local_by_name = {c.cell: c for c in local}
        if self.p4v_repo:
            try:
                p4v_cells = self.p4v_repo.list_cells(self.project)
            except Exception:
                p4v_cells = set()
            for name in p4v_cells:
                if name not in local_by_name:
                    # create placeholder meta for P4V-only cell
                    local_by_name[name] = QCCellMeta(
                        cell=name,
                        has_qcplan=False,
                        has_netlist=False,
                        has_data=False,
                        has_common_source=False,
                        has_ref=False,
                        delay_rows=0,
                        constraint_rows=0,
                    )
        merged = list(local_by_name.values())
        # sort by reversed lower-case cell name (legacy behavior)
        merged.sort(key=lambda c: c.cell.lower()[::-1])
        return merged

@dataclass
class GetCellDefaults:
    defaults_repo: QCDefaultsRepository
    def execute(self, project: str, subproject: str, cell: str, force: bool = False) -> QCDefaultPaths:
        return self.defaults_repo.derive_defaults(project, subproject, cell, force)

@dataclass
class ListTestbenches:
    tb_repo: QCTestbenchRepository
    def execute(self, project: str, subproject: str, cell: str) -> List[str]:
        return self.tb_repo.list_testbenches(project, subproject, cell)

@dataclass
class GetTestbenchStatus:
    tb_repo: QCTestbenchRepository
    def execute(self, testbench_dir: str) -> tuple[List[PVTRowMeta], str]:
        pvts = self.tb_repo.list_pvts(testbench_dir)
        overall = self._aggregate(pvts)
        return pvts, overall

    @staticmethod
    def _aggregate(pvts: List[PVTRowMeta]) -> str:
        if not pvts:
            return 'Not Started'
        statuses = {p.status for p in pvts}
        if 'Fail' in statuses:
            return 'Fail'
        if statuses == {'Passed'}:
            return 'Passed'
        if 'In Progress' in statuses:
            return 'In Progress'
        if statuses == {'Not Started'}:
            return 'Not Started'
        return 'Not Started'

@dataclass
class GenerateRunAllScript:
    script_builder: QCScriptBuilder
    def execute(self, cell: str, params: Dict[str, Any], project: str, subproject: str) -> str:
        return self.script_builder.build_runall(cell, params, project, subproject)

@dataclass
class BuildTables:
    tables_repo: QCTablesRepository
    def execute(self, timing_paths: str | None, data: str | None) -> Dict[str, List[TableRowData]]:
        return self.tables_repo.build_tables(timing_paths, data)


# ============================================================================
# Task Queue Use Cases (Phase 6)
# ============================================================================

@dataclass
class CreateTaskQueue:
    """Write task queue configuration files to cell directory."""
    
    def __init__(self, task_queue_repo):
        self.task_queue_repo = task_queue_repo
    
    def execute(self, cell_dir, project: str, subproject: str, cell: str, req):
        """Create or update task queue files.
        
        Args:
            cell_dir: Path to cell directory
            project: Project name
            subproject: Subproject name
            cell: Cell name
            req: TaskQueueRequest with configuration
            
        Returns:
            TaskQueueResult with paths and status
        """
        return self.task_queue_repo.write_task_queue(cell_dir, project, subproject, cell, req)


@dataclass
class GetTaskQueue:
    """Read existing task queue configuration."""
    
    def __init__(self, task_queue_repo):
        self.task_queue_repo = task_queue_repo
    
    def execute(self, cell_dir, project: str, subproject: str, cell: str):
        """Read task queue configuration from cell directory.
        
        Args:
            cell_dir: Path to cell directory
            project: Project name
            subproject: Subproject name
            cell: Cell name
            
        Returns:
            TaskQueueStatus with current configuration
        """
        return self.task_queue_repo.read_task_queue(cell_dir, project, subproject, cell)


__all__ = [
    "ListCells",
    "GetCellDefaults",
    "ListTestbenches",
    "GetTestbenchStatus",
    "GenerateRunAllScript",
    "BuildTables",
    "CreateTaskQueue",
    "GetTaskQueue",
]