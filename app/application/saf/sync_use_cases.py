"""Use cases for checking and syncing SAF config files from Perforce.

Migrated from legacy saf_service.py to follow Clean Architecture.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.domain.saf.repositories import SafCellRepository, SafPerforceRepository


@dataclass
class CheckAndSyncInstFileInput:
    """Input for checking and syncing inst/config files."""
    project: str
    subproject: str
    cell: str
    cell_type: str = "sis"  # "sis" or "nt"


@dataclass
class CheckAndSyncInstFileOutput:
    """Output from checking and syncing inst/config files."""
    synced: bool
    note: str
    error: Optional[str] = None


class CheckAndSyncInstFile:
    """Check if required config file exists in cell folder, sync from P4V if missing.
    
    For SiS cells, checks for .inst file and syncs from:
    //wwcad/msip/projects/ucie/<project>/<subproject>/design/timing/sis/<cellname>/
    
    For NT cells, checks for alphaNT.config file and syncs from:
    //wwcad/msip/projects/ucie/<project>/<subproject>/design/timing/nt/<cellname>/
    """
    
    def __init__(
        self,
        cell_repo: SafCellRepository,
        p4_repo: SafPerforceRepository
    ) -> None:
        self.cell_repo = cell_repo
        self.p4_repo = p4_repo
    
    def execute(self, inp: CheckAndSyncInstFileInput) -> CheckAndSyncInstFileOutput:
        """Execute the check and sync operation."""
        # Resolve cell root directory
        cell_root = self._resolve_cell_root(inp.project, inp.subproject, inp.cell, inp.cell_type)
        
        # Determine which file to check based on cell type
        if inp.cell_type == "nt":
            config_file = cell_root / "alphaNT.config"
            file_exists = config_file.exists()
            file_name = "alphaNT.config"
        else:
            # SiS cell - look for .inst file
            inst_files = list(cell_root.glob("*.inst"))
            file_exists = len(inst_files) > 0
            file_name = inst_files[0].name if inst_files else "*.inst"
        
        if file_exists:
            # Required file exists, no action needed
            return CheckAndSyncInstFileOutput(
                synced=False,
                note=f"✓ Found {file_name}",
                error=None
            )
        
        # Required file missing, sync from Perforce
        results = [f"⚠ No {file_name} found in {cell_root}"]
        
        sync_meta = self.p4_repo.sync_inst_file(
            inp.project,
            inp.subproject,
            inp.cell,
            inp.cell_type
        )
        
        if sync_meta.get("synced"):
            # Re-check existence after sync
            if inp.cell_type == "nt":
                file_exists_after = config_file.exists()
                found_file_name = file_name if file_exists_after else None
            else:
                inst_files_after = list(cell_root.glob("*.inst"))
                file_exists_after = len(inst_files_after) > 0
                found_file_name = inst_files_after[0].name if inst_files_after else None
            
            if file_exists_after:
                results.append(f"✓ Successfully synced, {found_file_name} found")
                return CheckAndSyncInstFileOutput(
                    synced=True,
                    note=" | ".join(results),
                    error=None
                )
            else:
                results.append(f"⚠ Sync completed but no {file_name} found")
                return CheckAndSyncInstFileOutput(
                    synced=True,
                    note=" | ".join(results),
                    error=f"No {file_name} found after sync"
                )
        else:
            err = sync_meta.get("error") or sync_meta.get("stderr") or "Unknown error"
            results.append(f"✗ P4V sync failed: {err}")
            return CheckAndSyncInstFileOutput(
                synced=False,
                note=" | ".join(results),
                error=f"P4V sync failed: {err}"
            )
    
    def _resolve_cell_root(
        self,
        project: str,
        subproject: str,
        cell: str,
        cell_type: str
    ) -> Path:
        """Resolve the cell root directory based on cell type."""
        if cell_type == "nt":
            root_str = self.cell_repo.resolve_nt_root(project, subproject)
            if not root_str:
                raise ValueError(f"NT root not found for {project}/{subproject}")
            cell_root = Path(root_str) / cell
        else:
            root_str = self.cell_repo.resolve_sis_root(project, subproject)
            if not root_str:
                raise ValueError(f"SiS root not found for {project}/{subproject}")
            cell_root = Path(root_str) / cell
        
        if not cell_root.exists():
            raise ValueError(f"Cell directory not found: {cell_root}")
        
        return cell_root


__all__ = [
    "CheckAndSyncInstFile",
    "CheckAndSyncInstFileInput",
    "CheckAndSyncInstFileOutput",
]
