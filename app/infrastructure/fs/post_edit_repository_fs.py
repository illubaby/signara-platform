"""Filesystem implementation of PostEditRepository.
Migrated logic from legacy app/services/post_edit_service.py
"""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.domain.post_edit.entities import PostEditCellMeta, CellMetricMeta
from app.domain.post_edit.repositories import PostEditRepository

POST_EDIT_SUBPATH = Path("design/timing/quality/1_postedit")
SIS_SUBPATH = Path("design/timing/sis")


def quality_base(project: str, subproject: str) -> Path:
    return PROJECTS_BASE / project / subproject / POST_EDIT_SUBPATH

class PostEditRepositoryFS(PostEditRepository):
    excluded_cell_dirs = {"release_final", "common", "logs", "backup_data", "bin"}

    def list_cells(self, project: str, subproject: str) -> List[PostEditCellMeta]:
        sis_root = PROJECTS_BASE / project / subproject / SIS_SUBPATH
        cells: List[PostEditCellMeta] = []
        if not sis_root.exists():
            return cells
        for entry in sorted(sis_root.iterdir(), key=lambda p: p.name.lower()):
            if not entry.is_dir():
                continue
            name = entry.name
            if name in self.excluded_cell_dirs:
                continue
            cfg = entry / f"{name}.cfg"
            cells.append(PostEditCellMeta(cell=name, config_path=str(cfg), exists=cfg.is_file()))
        return cells

    def compute_metrics(self, project: str, subproject: str, lib_path: Optional[str]) -> List[CellMetricMeta]:
        sis_root = PROJECTS_BASE / project / subproject / SIS_SUBPATH
        updated_dir = quality_base(project, subproject) / "UpdatedLibs"
        cell_names: List[str] = []
        if sis_root.exists():
            cell_names = [p.name for p in sis_root.iterdir() if p.is_dir() and p.name not in {"release_final", "common", "logs"}]
            cell_names.sort()
        lib_root = Path(lib_path) if lib_path else None
        result: List[CellMetricMeta] = []
        for cell in cell_names:
            a_count = 0
            if lib_root:
                cell_lib_dir = lib_root / cell
                if cell_lib_dir.exists():
                    a_count = len([p for p in cell_lib_dir.glob("*.lib") if p.is_file()])
            upd_count = 0
            cell_upd_dir = updated_dir / cell
            if cell_upd_dir.exists():
                upd_count = len([p for p in cell_upd_dir.glob("*.lib") if p.is_file()])
            elif updated_dir.exists():
                upd_count = len([p for p in updated_dir.glob(f"{cell}*.lib") if p.is_file()])
            result.append(CellMetricMeta(cell=cell, a_libs_count=a_count, updated_libs_count=upd_count, complete=upd_count >= 16))
        return result

__all__ = ["PostEditRepositoryFS", "quality_base"]
