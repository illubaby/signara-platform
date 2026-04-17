"""Filesystem implementation of SafCellRepository (Phase 2).

Moves pure/local filesystem logic out of legacy saf_service.
Perforce-related logic remains elsewhere and will be migrated in a later phase.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import re

from app.domain.saf.entities import Cell
from app.domain.saf.repositories import SafCellRepository
from app.infrastructure.fs.project_root import PROJECTS_BASE

class _Config:
    base_override: Optional[Path] = None

def set_projects_base_override(path: Path) -> None:
    """Override PROJECTS_BASE for testing (not used in production)."""
    _Config.base_override = path


def _safe_listdir(path: Path) -> List[Path]:
    try:
        if path.exists() and path.is_dir():
            return list(path.iterdir())
    except Exception:
        return []
    return []


class SafCellRepositoryFS(SafCellRepository):
    """Concrete filesystem repository for SAF cell operations."""

    def resolve_sis_root(self, project: str, subproject: str) -> Optional[str]:
        base_root = _Config.base_override if _Config.base_override else PROJECTS_BASE
        base = base_root / project / subproject
        patterns = [
            base / "design" / "timing" / "sis",
            base / "design" / "timing" / "SiS",
            base / "timing" / "sis",
            base / "timing" / "SiS",
        ]
        for p in patterns:
            if p.exists() and p.is_dir():
                return str(p)
        # fallback search
        try:
            for level1 in base.iterdir():
                if level1.is_dir():
                    test = level1 / "timing" / "sis"
                    if test.exists() and test.is_dir():
                        return str(test)
        except Exception:
            pass
        return None

    def resolve_nt_root(self, project: str, subproject: str) -> Optional[str]:
        base_root = _Config.base_override if _Config.base_override else PROJECTS_BASE
        base = base_root / project / subproject
        patterns = [
            base / "design" / "timing" / "nt",
            base / "design" / "timing" / "NT",
            base / "timing" / "nt",
            base / "timing" / "NT",
        ]
        for p in patterns:
            if p.exists() and p.is_dir():
                return str(p)
        try:
            for level1 in base.iterdir():
                if level1.is_dir():
                    test = level1 / "timing" / "nt"
                    if test.exists() and test.is_dir():
                        return str(test)
        except Exception:
            pass
        return None

    def list_local_cells(self, project: str, subproject: str, cell_type: str) -> List[Cell]:
        root_str = self.resolve_nt_root(project, subproject) if cell_type == "nt" else self.resolve_sis_root(project, subproject)
        if not root_str:
            return []
        root = Path(root_str)
        cells: List[Cell] = []
        for entry in _safe_listdir(root):
            if not entry.is_dir():
                continue
            name = entry.name
            if cell_type == "nt":
                if not (entry / "alphaNT.config").exists():
                    continue
            else:
                inst_files = list(entry.glob("*.inst"))
                if not inst_files:
                    continue
            pvts = self.collect_pvts(str(entry))
            cells.append(Cell(
                cell=name,
                type=cell_type,
                pvts=pvts,
                pvt_count=len(pvts),
                netlist_version=self.netlist_version(project, subproject, name, cell_type),
                final_libs=self.final_lib_count(root, name) if cell_type == "sis" else 0,
            ))
        cells.sort(key=lambda c: c.cell.lower())
        return cells

    def collect_pvts(self, cell_dir: str) -> List[str]:
        pvts: List[str] = []
        base = Path(cell_dir)
        for entry in _safe_listdir(base):
            if entry.is_dir() and entry.name.startswith("char_") and len(entry.name) > 5:
                pvts.append(entry.name[5:])
        return sorted(pvts)

    def collect_nt_pvts(self, project: str, subproject: str, cell: str) -> List[str]:
        base_root = _Config.base_override if _Config.base_override else PROJECTS_BASE
        pvt_file = base_root / project / subproject / "design" / "timing" / "nt" / cell / "pvt_corners.lst"
        if not pvt_file.exists():
            return []
        pvts: List[str] = []
        try:
            with pvt_file.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        pvts.append(line)
        except Exception:
            return []
        return sorted(pvts)

    def netlist_version(self, project: str, subproject: str, cell: str, cell_type: str) -> str:
        base_root = _Config.base_override if _Config.base_override else PROJECTS_BASE
        extr_cell_dir = base_root / project / subproject / "design" / "timing" / "extr" / cell
        if not extr_cell_dir.exists():
            return "Missing"
        if cell_type == "nt":
            target_dir = extr_cell_dir / "nt" / "etm"
        else:
            target_dir = extr_cell_dir / "sis"
        # Collect candidate netlist files (.sp or .spf) with patterns:
        #   {cell}.sp / {cell}.spf / {cell}_*.sp / {cell}_*.spf
        netlist_files: List[Path] = []
        try:
            if target_dir.exists():
                patterns = [f"{cell}.sp", f"{cell}.spf", f"{cell}_*.sp", f"{cell}_*.spf"]
                for patt in patterns:
                    netlist_files.extend(list(target_dir.glob(patt)))
        except Exception:
            netlist_files = []
        # Fallback: scan base extraction cell directory for same patterns if none found in target
        if not netlist_files:
            try:
                if extr_cell_dir.exists():
                    for p in extr_cell_dir.iterdir():
                        if p.is_file() and p.suffix in (".sp", ".spf"):
                            name = p.name
                            if name == f"{cell}.sp" or name == f"{cell}.spf" or name.startswith(f"{cell}_"):
                                netlist_files.append(p)
            except Exception:
                netlist_files = []
        if not netlist_files:
            return "Missing"
        file_versions: dict[str, int] = {}
        for nf in netlist_files:
            try:
                with nf.open("r", errors="ignore") as f:
                    for line in f:
                        if "snapHier.txt" in line and "#" in line:
                            matches = re.findall(r"#(\d+)", line)
                            if matches:
                                file_versions[nf.name] = int(matches[0])
                                break
            except Exception:
                continue
        if not file_versions:
            return "nolpe"
        unique = set(file_versions.values())
        if len(unique) > 1:
            min_ver = min(unique); max_ver = max(unique)
            min_adj = min_ver - 1 if min_ver > 0 else min_ver
            max_adj = max_ver - 1 if max_ver > 0 else max_ver
            return f"Mismatch: #{min_adj}-#{max_adj}"
        version = next(iter(unique))
        adj = version - 1 if version > 0 else version
        return f"#{adj}"

    def final_lib_count(self, sis_root: Path, cell: str) -> int:
        total = 0
        try:
            cell_dir = sis_root / cell
            for sub in ("lib", "lib_pg"):
                d = cell_dir / sub
                if not d.exists() or not d.is_dir():
                    continue
                try:
                    for p in d.iterdir():
                        if p.is_file() and p.name.endswith(".lib"):
                            total += 1
                except Exception:
                    continue
        except Exception:
            return total
        return total

__all__ = ["SafCellRepositoryFS", "set_projects_base_override"]
