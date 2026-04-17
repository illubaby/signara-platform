"""Port definitions (Protocols) for Post-Edit feature.
Application layer depends on these, infrastructure implements them.
"""
from __future__ import annotations
from typing import Protocol, List, Optional
from .entities import PostEditCellMeta, CellMetricMeta

class PostEditRepository(Protocol):
    def list_cells(self, project: str, subproject: str) -> List[PostEditCellMeta]: ...
    def compute_metrics(self, project: str, subproject: str, lib_path: Optional[str]) -> List[CellMetricMeta]: ...

__all__ = ["PostEditRepository"]
