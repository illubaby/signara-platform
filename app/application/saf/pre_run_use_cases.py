"""Pre-run SAF use-cases: directory creation, config (.inst/alphaNT.config) presence, netlist presence.

Phase 1 migration: logic extracted from legacy router & saf_service.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
from app.application.saf.netlist_use_cases import SyncNetlist, SyncNetlistInput

# INPUT / OUTPUT DATACLASSES

@dataclass
class EnsureCellDirectoriesInput:
    project: str
    subproject: str
    cell: str
    cell_type: str  # 'sis' or 'nt'

@dataclass
class EnsureCellDirectoriesOutput:
    root_created: bool
    cell_created: bool
    cell_root: Path
    cell_dir: Path
    note: str

@dataclass
class EnsureCellConfigInput:
    project: str
    subproject: str
    cell: str
    cell_type: str
    cell_dir: Path

@dataclass
class EnsureCellConfigOutput:
    synced: bool
    file_found: bool
    file_name: Optional[str]
    note: str
    error: Optional[str] = None

@dataclass
class EnsureNetlistPresentInput:
    project: str
    subproject: str
    cell: str
    cell_type: str
    cell_dir: Path

@dataclass
class EnsureNetlistPresentOutput:
    synced: bool
    found: bool
    netlist_version: Optional[str]
    checked_path: Path
    note: str
    error: Optional[str] = None

# USE-CASES

class EnsureCellDirectories:
    def __init__(self, repo: Optional[SafCellRepositoryFS] = None):
        self.repo = repo or SafCellRepositoryFS()

    def execute(self, inp: EnsureCellDirectoriesInput) -> EnsureCellDirectoriesOutput:
        if inp.cell_type not in ("sis", "nt"):
            raise ValueError(f"Invalid cell_type {inp.cell_type}")
        # Determine root path via repository convenience methods
        root: Optional[str]
        if inp.cell_type == "sis":
            root = self.repo.resolve_sis_root(inp.project, inp.subproject)
            target_root = PROJECTS_BASE / inp.project / inp.subproject / "design" / "timing" / "sis"
        else:
            root = self.repo.resolve_nt_root(inp.project, inp.subproject)
            target_root = PROJECTS_BASE / inp.project / inp.subproject / "design" / "timing" / "nt"
        root_created = False
        if root is None:
            target_root.mkdir(parents=True, exist_ok=True)
            root_created = True
            root = str(target_root)
        cell_root = Path(root)
        cell_dir = cell_root / inp.cell
        cell_created = False
        if not cell_dir.exists():
            cell_dir.mkdir(parents=True, exist_ok=True)
            cell_created = True
        note = ", ".join([
            f"root_created={root_created}",
            f"cell_created={cell_created}",
            f"cell_root={cell_root}",
            f"cell_dir={cell_dir}",
        ])
        return EnsureCellDirectoriesOutput(root_created, cell_created, cell_root, cell_dir, note)

class EnsureCellConfig:
    def __init__(self, p4_repo: Optional[SafPerforceRepositoryP4] = None):
        self.p4_repo = p4_repo or SafPerforceRepositoryP4()

    def execute(self, inp: EnsureCellConfigInput) -> EnsureCellConfigOutput:
        if inp.cell_type == "nt":
            target_file = inp.cell_dir / "alphaNT.config"
            pattern_desc = "alphaNT.config"
            file_found = target_file.exists()
        else:
            inst_files = list(inp.cell_dir.glob("*.inst"))
            file_found = len(inst_files) > 0
            target_file = inst_files[0] if inst_files else None
            pattern_desc = "*.inst"
        if file_found:
            return EnsureCellConfigOutput(False, True, target_file.name if target_file else pattern_desc, f"Found {pattern_desc}", None)
        # perform sync
        sync_meta = self.p4_repo.sync_inst_file(inp.project, inp.subproject, inp.cell, inp.cell_type)
        # re-check
        if inp.cell_type == "nt":
            file_found_after = (inp.cell_dir / "alphaNT.config").exists()
            fname = "alphaNT.config" if file_found_after else None
        else:
            inst_files_after = list(inp.cell_dir.glob("*.inst"))
            file_found_after = len(inst_files_after) > 0
            fname = inst_files_after[0].name if inst_files_after else None
        if file_found_after:
            return EnsureCellConfigOutput(sync_meta.get("synced", False), True, fname, "Config synced", None)
        else:
            err = sync_meta.get("error") or sync_meta.get("stderr") or "Unknown sync failure"
            return EnsureCellConfigOutput(sync_meta.get("synced", False), False, None, "Config sync attempted but not found", err)

class EnsureNetlistPresent:
    def __init__(self, p4_repo: Optional[SafPerforceRepositoryP4] = None):
        self.p4_repo = p4_repo or SafPerforceRepositoryP4()
        self.sync_uc = SyncNetlist(self.p4_repo)

    def execute(self, inp: EnsureNetlistPresentInput) -> EnsureNetlistPresentOutput:
        # Netlists are synced from the design/timing/extr depot tree.
        extr_root = PROJECTS_BASE / inp.project / inp.subproject / "design" / "timing" / "extr" / inp.cell
        checked_path = extr_root / "nt" / "etm" if inp.cell_type == "nt" else extr_root / "sis"
        found = checked_path.exists()
        if found:
            return EnsureNetlistPresentOutput(False, True, None, checked_path, f"Netlist present at {checked_path}")
        # Do NOT auto-sync on run; only report missing.
        return EnsureNetlistPresentOutput(False, False, None, checked_path, f"Netlist missing at {checked_path}")

__all__ = [
    "EnsureCellDirectories", "EnsureCellDirectoriesInput", "EnsureCellDirectoriesOutput",
    "EnsureCellConfig", "EnsureCellConfigInput", "EnsureCellConfigOutput",
    "EnsureNetlistPresent", "EnsureNetlistPresentInput", "EnsureNetlistPresentOutput",
]
