"""Filesystem implementation of QCCellRepository.

Responsible only for local filesystem scanning of QC cells.
P4V integration lives in separate repository.
"""
from __future__ import annotations
from pathlib import Path
from typing import List
from app.domain.qc.entities import QCCellMeta
from app.domain.qc.repositories import QCCellRepository
import app.infrastructure.fs.project_root as project_root

QC_SUBPATH = Path("design/timing/quality/4_qc")

class QCCellRepositoryFS(QCCellRepository):
    def list_local_cells(self, project: str, subproject: str) -> List[QCCellMeta]:
        root = project_root.PROJECTS_BASE / project / subproject / QC_SUBPATH
        if not root.exists():
            return []
        cells: List[QCCellMeta] = []
        for entry in root.iterdir():
            if not entry.is_dir():
                continue
            cells.append(QCCellMeta(
                cell=entry.name,
                has_qcplan=any(p.name.endswith('_QcPlan.xlsx') for p in entry.glob('*_QcPlan.xlsx')),
                has_netlist=(entry / 'netlist.txt').exists(),
                has_data=(entry / 'data').exists(),
                has_common_source=(entry / 'common_source').exists(),
                has_ref=(entry / 'ref').exists(),
                delay_rows=0,  # populated later by tables use-case
                constraint_rows=0,
            ))
        return cells

    def list_all_cells(self, project: str, subproject: str) -> List[QCCellMeta]:
        # In Phase 1 the merge logic lives in application layer, so here we just return local.
        return self.list_local_cells(project, subproject)

__all__ = ["QCCellRepositoryFS"]