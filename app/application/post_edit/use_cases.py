"""Application use-cases for Post-Edit feature.
Provide orchestration and filtering without exposing infrastructure or FastAPI specifics.
"""
from __future__ import annotations
from typing import List, Optional

from app.domain.post_edit.repositories import PostEditRepository
from app.domain.post_edit.entities import PostEditCellMeta, CellMetricMeta

class ListPostEditCells:
    def __init__(self, repo: PostEditRepository):
        self.repo = repo

    def execute(self, project: str, subproject: str, include_missing: bool = False) -> List[PostEditCellMeta]:
        cells = self.repo.list_cells(project, subproject)
        if include_missing:
            return cells
        return [c for c in cells if c.exists]

class GetPostEditMetrics:
    def __init__(self, repo: PostEditRepository):
        self.repo = repo

    def execute(self, project: str, subproject: str, lib_path: Optional[str], include_missing: bool = False) -> List[CellMetricMeta]:
        metrics = self.repo.compute_metrics(project, subproject, lib_path)
        # Filter based on existing config unless include_missing requested
        if include_missing:
            return metrics
        existing_cells = {c.cell for c in self.repo.list_cells(project, subproject) if c.exists}
        return [m for m in metrics if m.cell in existing_cells]

__all__ = ["ListPostEditCells", "GetPostEditMetrics"]
