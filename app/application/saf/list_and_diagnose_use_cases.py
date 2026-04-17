"""ListSafCells & DiagnoseSaf application use-cases (Phase 5).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional
from pathlib import Path

from app.domain.saf.repositories import SafCellRepository, SafPerforceRepository
from app.infrastructure.fs.pvt_status_repository_fs import PvtStatusRepositoryFS
from .ttl_cache import TTLCache
from app.domain.saf.entities import Cell

@dataclass
class ListSafCellsInput:
    project: str
    subproject: str
    force_refresh: bool = False

@dataclass
class ListSafCellsOutput:
    cells: List[Cell]
    sis_root: Optional[str]
    nt_root: Optional[str]
    sis_candidates: List[str]
    nt_candidates: List[str]
    note: str

class ListSafCells:
    def __init__(self, fs_repo: SafCellRepository, p4_repo: SafPerforceRepository, cache: TTLCache) -> None:
        self.fs_repo = fs_repo
        self.p4_repo = p4_repo
        self.cache = cache

    def execute(self, inp: ListSafCellsInput) -> ListSafCellsOutput:
        cache_key = f"saf:list:{inp.project}:{inp.subproject}"
        cached = None if inp.force_refresh else self.cache.get(cache_key)
        sis_root = self.fs_repo.resolve_sis_root(inp.project, inp.subproject)
        nt_root = self.fs_repo.resolve_nt_root(inp.project, inp.subproject)
        sis_candidates = [sis_root] if sis_root else []
        nt_candidates = [nt_root] if nt_root else []
        if cached is not None:
            return ListSafCellsOutput(cells=cached, sis_root=sis_root, nt_root=nt_root, sis_candidates=sis_candidates, nt_candidates=nt_candidates, note="from cache")
        # Local cells
        local_sis = self.fs_repo.list_local_cells(inp.project, inp.subproject, "sis") if sis_root else []
        local_nt = self.fs_repo.list_local_cells(inp.project, inp.subproject, "nt") if nt_root else []
        cell_map: Dict[str, Cell] = {c.cell: c for c in local_sis + local_nt}
        # Depot cells
        try:
            depot_cells = self.p4_repo.list_depot_cells(inp.project, inp.subproject)
            for name, ctype in depot_cells.items():
                if name not in cell_map:
                    # create minimal cell stub; pvts fetched lazily
                    cell_map[name] = Cell(cell=name, type=ctype, pvts=[], pvt_count=0, netlist_version=self.fs_repo.netlist_version(inp.project, inp.subproject, name, ctype), final_libs=0)
        except Exception:
            pass
        cells = list(cell_map.values())
        cells.sort(key=lambda c: (c.type != 'sis', c.cell.lower()))
        self.cache.set(cache_key, cells)
        return ListSafCellsOutput(cells=cells, sis_root=sis_root, nt_root=nt_root, sis_candidates=sis_candidates, nt_candidates=nt_candidates, note="fresh scan")

@dataclass
class DiagnoseSafInput:
    project: str
    subproject: str

@dataclass
class DiagnoseSafOutput:
    sis_root: Optional[str]
    candidate_paths: List[str]
    sis_root_exists: bool
    sample_entries: List[str]
    char_dirs_found: int
    first_char_dirs: List[str]

class DiagnoseSaf:
    def __init__(self, fs_repo: SafCellRepository) -> None:
        self.fs_repo = fs_repo

    def execute(self, inp: DiagnoseSafInput) -> DiagnoseSafOutput:
        sis_root = self.fs_repo.resolve_sis_root(inp.project, inp.subproject)
        candidate_paths = [sis_root] if sis_root else []
        sample_entries: List[str] = []
        char_dirs: List[str] = []
        char_count = 0
        if sis_root and Path(sis_root).exists():
            try:
                for entry in list(Path(sis_root).iterdir())[:50]:
                    mark = []
                    if entry.is_dir():
                        mark.append('D')
                        if entry.name.startswith('char_'):
                            char_count += 1
                            if len(char_dirs) < 10:
                                char_dirs.append(entry.name)
                    else:
                        mark.append('F')
                    sample_entries.append(f"{entry.name} [{' '.join(mark)}]")
            except Exception as e:
                sample_entries.append(f"<error reading dir: {e}>")
        return DiagnoseSafOutput(
            sis_root=sis_root,
            candidate_paths=candidate_paths,
            sis_root_exists=bool(sis_root and Path(sis_root).exists()),
            sample_entries=sample_entries,
            char_dirs_found=char_count,
            first_char_dirs=char_dirs,
        )

__all__ = [
    "ListSafCells", "ListSafCellsInput", "ListSafCellsOutput",
    "DiagnoseSaf", "DiagnoseSafInput", "DiagnoseSafOutput"
]
