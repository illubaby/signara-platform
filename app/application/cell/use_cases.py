"""Use cases for Cell feature.

Orchestrates fetching and processing cell information from ProjectInfo.xlsx.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from pathlib import Path
import re
import os
import logging

from app.domain.cell.entities import Cell
from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.domain.saf.repositories import SafPerforceRepository


logger = logging.getLogger(__name__)


@dataclass
class ListCellsOutput:
    """Output for ListCells use case."""
    cells: List[Cell]
    sis_count: int
    nt_count: int
    total_count: int


class ListCells:
    """
    Use case to list all cells from ProjectInfo.xlsx.
    
    Fetches cells from Perforce depot and categorizes them by type.
    """
    
    def __init__(self, cells: List[Cell]) -> None:
        self.cells = cells
    
    def execute(self) -> ListCellsOutput:
        """
        Execute the use case to process cells.
        
        Returns:
            Output with cells list and statistics
        """
        # Calculate statistics
        sis_count = sum(1 for c in self.cells if c.tool.lower() == "sis")
        nt_count = sum(1 for c in self.cells if c.tool.lower() == "nt")
        
        # Sort by cell name
        self.cells.sort(key=lambda c: c.ckt_macros.lower())
        
        return ListCellsOutput(
            cells=self.cells,
            sis_count=sis_count,
            nt_count=nt_count,
            total_count=len(self.cells)
        )


def list_local_int_cells(project: str, subproject: str) -> List[str]:
    """List local INT cells from NT folder.

    Looks under `<PROJECTS_BASE>/<project>/<subproject>/design/timing/nt` for
    directories ending with `_int` and returns their full names (with suffix).

    Example: returns `dwc_ucie3phy_lcdl_ew_int`.
    """
    try:
        nt_root = PROJECTS_BASE / project / subproject / "design" / "timing" / "nt"
        if not nt_root.exists() or not nt_root.is_dir():
            return []
        names: List[str] = []
        for entry in nt_root.iterdir():
            if entry.is_dir():
                name = entry.name
                if name.endswith("_int"):
                    names.append(name)
        names.sort()
        return names
    except Exception:
        return []


@dataclass
class PrepareIntCellInput:
    project: str
    subproject: str
    cell_base: str  # without trailing _int

@dataclass
class PrepareIntCellOutput:
    project: str
    subproject: str
    cell_dir: str
    created: bool
    synced: bool
    note: str

class PrepareIntCell:
    """Ensure local INT cell directory exists and sync contents from Perforce.

    Folder: design/timing/nt/<cell_base>_int
    Uses Perforce repo sync (treated as NT path) after creating directory if missing.
    """
    def __init__(self, p4_repo: SafPerforceRepository) -> None:
        self.p4_repo = p4_repo

    def execute(self, inp: PrepareIntCellInput) -> PrepareIntCellOutput:
        cell_name = f"{inp.cell_base}_int" if not inp.cell_base.endswith("_int") else inp.cell_base
        nt_root = PROJECTS_BASE / inp.project / inp.subproject / "design" / "timing" / "nt"
        cell_dir = nt_root / cell_name
        created = False
        logger.info(
            "[PrepareIntCell] start project=%s subproject=%s requested_cell=%s mapped_cell=%s nt_root=%s mapped_dir=%s",
            inp.project,
            inp.subproject,
            inp.cell_base,
            cell_name,
            str(nt_root),
            str(cell_dir),
        )
        try:
            nt_root.mkdir(parents=True, exist_ok=True)
            if not cell_dir.exists():
                cell_dir.mkdir(parents=True, exist_ok=True)
                created = True
                logger.info("[PrepareIntCell] created mapped_dir=%s", str(cell_dir))
            else:
                logger.info("[PrepareIntCell] mapped_dir already exists=%s", str(cell_dir))
        except Exception as e:
            logger.exception("[PrepareIntCell] failed creating mapped dir=%s", str(cell_dir))
            return PrepareIntCellOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell_dir=str(cell_dir),
                created=False,
                synced=False,
                note=f"Failed to create directory: {e}"
            )
        config_path = cell_dir / "alphaNT.config"
        need_sync = created or (not config_path.exists())
        logger.info(
            "[PrepareIntCell] config_check path=%s exists=%s need_sync=%s reason=%s",
            str(config_path),
            config_path.exists(),
            need_sync,
            "created" if created else ("missing_alphaNT.config" if not config_path.exists() else "skip"),
        )

        if not need_sync:
            logger.info("[PrepareIntCell] skip sync because alphaNT.config already present")
            return PrepareIntCellOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell_dir=str(cell_dir),
                created=False,
                synced=False,
                note="exists (alphaNT.config present; skip sync)"
            )

        try:
            sync = self.p4_repo.sync_inst_file(inp.project, inp.subproject, cell_name, "nt")
            synced = bool(sync.get("synced"))
            has_config_after = config_path.exists()
            logger.info(
                "[PrepareIntCell] sync_result synced=%s has_config_after=%s stderr=%s error=%s",
                synced,
                has_config_after,
                sync.get("stderr"),
                sync.get("error"),
            )
            if synced and has_config_after:
                note = "synced"
            elif synced and not has_config_after:
                note = "sync attempted but alphaNT.config still missing"
                synced = False
            else:
                note = sync.get("error") or "sync failed"
        except Exception as e:
            logger.exception("[PrepareIntCell] sync exception mapped_cell=%s mapped_dir=%s", cell_name, str(cell_dir))
            return PrepareIntCellOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell_dir=str(cell_dir),
                created=created,
                synced=False,
                note=f"Sync error: {e}"
            )
        logger.info(
            "[PrepareIntCell] done mapped_cell=%s mapped_dir=%s created=%s synced=%s note=%s",
            cell_name,
            str(cell_dir),
            created,
            synced,
            note,
        )
        return PrepareIntCellOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell_dir=str(cell_dir),
            created=created,
            synced=synced,
            note=note,
        )


@dataclass
class GetNetlistVersionInput:
    """Input for GetNetlistVersion use case."""
    project: str
    subproject: str
    cell: str
    cell_type: str  # "sis" or "nt"
    pic: Optional[str] = None  # PIC username to resolve their workspace


@dataclass
class GetNetlistVersionOutput:
    """Output for GetNetlistVersion use case."""
    cell: str
    cell_type: str
    netlist_version: str


class GetNetlistVersion:
    """
    Use case to determine netlist version (snaphier) for a cell.
    
    Logic copied from SAF timing page implementation:
    - Searches for netlist files (.sp, .spf) in extraction directory
    - Parses snapHier.txt references to extract version numbers
    - Returns version string in format "#N" or error states like "Missing", "nolpe", "Mismatch"
    """
    
    def _resolve_pic_workspace(self, pic: str) -> Path:
        """
        Resolve the PROJECTS_BASE path for a specific PIC user.
        
        On Windows: C:/Users/{pic}/Perforce/{pic}_SNPS/wwcad/msip/projects/ucie
        On Linux: /u/{pic}/p4_ws/projects/ucie
        """
        if os.name == 'nt':  # Windows
            return Path(f"C:/Users/{pic}/Perforce/{pic}_SNPS/wwcad/msip/projects/ucie")
        else:  # Linux
            return Path(f"/u/{pic}/p4_ws/projects/ucie")
    
    def execute(self, inp: GetNetlistVersionInput) -> GetNetlistVersionOutput:
        """
        Determine netlist version for a given cell.
        
        Args:
            inp: Input containing project, subproject, cell name, cell type, and optional PIC
            
        Returns:
            Output with netlist version string
        """
        # Use PIC's workspace if provided, otherwise use current user's workspace
        base_path = self._resolve_pic_workspace(inp.pic)
        extr_cell_dir = base_path / inp.project / inp.subproject / "design" / "timing" / "extr" / inp.cell
        
        if not extr_cell_dir.exists():
            return GetNetlistVersionOutput(
                cell=inp.cell,
                cell_type=inp.cell_type,
                netlist_version="Missing"
            )
        
        # Determine target directory based on cell type
        if inp.cell_type.lower() == "nt":
            target_dir = extr_cell_dir / "nt" / "etm"
        else:
            target_dir = extr_cell_dir / "sis"
        
        # Collect candidate netlist files (.sp or .spf) with patterns:
        # {cell}.sp / {cell}.spf / {cell}_*.sp / {cell}_*.spf
        netlist_files: List[Path] = []
        try:
            if target_dir.exists():
                patterns = [f"{inp.cell}.sp", f"{inp.cell}.spf", f"{inp.cell}_*.sp", f"{inp.cell}_*.spf"]
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
                            if name == f"{inp.cell}.sp" or name == f"{inp.cell}.spf" or name.startswith(f"{inp.cell}_"):
                                netlist_files.append(p)
            except Exception:
                netlist_files = []
        
        if not netlist_files:
            return GetNetlistVersionOutput(
                cell=inp.cell,
                cell_type=inp.cell_type,
                netlist_version="Missing"
            )
        
        # Parse each file to find snapHier version
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
            return GetNetlistVersionOutput(
                cell=inp.cell,
                cell_type=inp.cell_type,
                netlist_version="nolpe"
            )
        
        # Check for version consistency
        unique = set(file_versions.values())
        if len(unique) > 1:
            min_ver = min(unique)
            max_ver = max(unique)
            min_adj = min_ver - 1 if min_ver > 0 else min_ver
            max_adj = max_ver - 1 if max_ver > 0 else max_ver
            return GetNetlistVersionOutput(
                cell=inp.cell,
                cell_type=inp.cell_type,
                netlist_version=f"Mismatch: #{min_adj}-#{max_adj}"
            )
        
        # Return consistent version (adjusted by -1)
        version = next(iter(unique))
        adj = version - 1 if version > 0 else version
        return GetNetlistVersionOutput(
            cell=inp.cell,
            cell_type=inp.cell_type,
            netlist_version=f"#{adj}"
        )


@dataclass
class GetCellPvtStatusInput:
    """Input for GetCellPvtStatus use case."""
    project: str
    subproject: str
    cell: str
    cell_type: str  # "sis" or "nt"
    pic: Optional[str] = None  # PIC username to resolve their workspace


@dataclass
class GetCellPvtStatusOutput:
    """Output for GetCellPvtStatus use case."""
    cell: str
    cell_type: str
    statuses: dict[str, str]  # PVT name -> status (success/fail/in_progress/idle)
    summary: dict[str, int]  # passed/failed/in_progress/not_started counts


class GetCellPvtStatus:
    """
    Use case to determine PVT status for a cell in Project Status page.
    
    Similar to SAF PVT Status but adapted for Project Status context.
    Scans cell directories and analyzes log files to determine characterization status.
    """
    
    MAX_LOG_BYTES = 2_000_000
    
    def _resolve_pic_workspace(self, pic: str) -> Path:
        """
        Resolve the PROJECTS_BASE path for a specific PIC user.
        
        On Windows: C:/Users/{pic}/Perforce/{pic}_SNPS/wwcad/msip/projects/ucie
        On Linux: /u/{pic}/p4_ws/projects/ucie
        """
        if os.name == 'nt':  # Windows
            return Path(f"C:/Users/{pic}/Perforce/{pic}_SNPS/wwcad/msip/projects/ucie")
        else:  # Linux
            return Path(f"/u/{pic}/p4_ws/projects/ucie")
    
    def _determine_status(self, pvt_dir: Path, is_nt: bool) -> str:
        """
        Determine PVT status for SiS or NT cells.
        
        Args:
            pvt_dir: Path to PVT directory (char_<PVT> for SiS, Run_<PVT>_etm_<number> for NT)
            is_nt: True if this is an NT cell, False for SiS cell
            
        Returns:
            Status string: "success", "fail", "in_progress", or "idle"
        """
        if is_nt:
            # NT cell: check timing.log for "Diagnostics summary:" line
            timing_log = pvt_dir / "timing.log"
            
            if not timing_log.exists():
                return "idle"
            
            # Check for "Diagnostics summary:" line
            found_diagnostics_line = False
            has_error = False
            
            try:
                with timing_log.open("r", errors="ignore") as fh:
                    for line in fh:
                        if "Diagnostics summary:" in line:
                            found_diagnostics_line = True
                            if "error" in line.lower():
                                has_error = True
                            break
            except Exception:
                return "in_progress"
            
            if not found_diagnostics_line:
                return "in_progress"
            
            return "fail" if has_error else "success"
        else:
            # SiS cell: check primelib.log and siliconsmart.log
            status_file_correct = pvt_dir / "statusComplete"
            status_file_legacy = pvt_dir / "statusComplele"
            logs = [pvt_dir / "primelib.log", pvt_dir / "siliconsmart.log"]
            existing_logs = [lg for lg in logs if lg.exists()]
            
            if not existing_logs:
                return "idle"
            
            found_error = False
            found_shutdown = False
            
            for log in existing_logs:
                processed = 0
                try:
                    with log.open("r", errors="ignore") as fh:
                        for line in fh:
                            stripped = line.lstrip()
                            if stripped.startswith("Error ") or stripped.startswith("Error:") or \
                               stripped.startswith("ERROR ") or stripped.startswith("ERROR:"):
                                found_error = True
                                break
                            if "Shutting down modules" in line:
                                found_shutdown = True
                            processed += len(line.encode("utf-8", "ignore"))
                            if processed > self.MAX_LOG_BYTES or (found_shutdown and found_error):
                                break
                except Exception:
                    continue
                if found_error:
                    break
            
            if found_error:
                return "fail"
            if (status_file_correct.exists() or status_file_legacy.exists()) and found_shutdown:
                return "success"
            return "in_progress"
    
    def _get_statuses_for_cell(self, cell_dir: Path, is_nt: bool) -> dict[str, str]:
        """
        Get PVT statuses for a cell.
        
        Args:
            cell_dir: Path to cell directory
            is_nt: True if this is an NT cell, False for SiS cell
            
        Returns:
            Dictionary mapping PVT name to status string
        """
        statuses: dict[str, str] = {}
        if not cell_dir.exists() or not cell_dir.is_dir():
            return statuses
        if is_nt:
            # NT cell: check ScratchDir/timing/<PVT>/ directories
            scratch_timing = cell_dir / "ScratchDir" / "timing"            
            if not scratch_timing.exists() or not scratch_timing.is_dir():
                return statuses
            # Directory format: Run_<base_pvt_name>_etm_<number>
            for entry in scratch_timing.iterdir():
                if entry.is_dir():
                    dir_name = entry.name
                    
                    # Extract base PVT name by removing Run_ prefix and _etm_<number> suffix
                    base_pvt_name = dir_name
                    if base_pvt_name.startswith("Run_"):
                        base_pvt_name = base_pvt_name[4:]
                    if "_etm_" in base_pvt_name:
                        base_pvt_name = base_pvt_name.rsplit("_etm_", 1)[0]
                    
                    try:
                        
                        status = self._determine_status(entry, is_nt=True)
                        # Store with base name, prioritize success/fail over idle
                        if base_pvt_name not in statuses or status in ('success', 'fail', 'in_progress'):
                            statuses[base_pvt_name] = status
                    except Exception:
                        if base_pvt_name not in statuses:
                            statuses[base_pvt_name] = "in_progress"
        else:
            # SiS cell: check char_<PVT> directories
            for entry in cell_dir.iterdir():
                if entry.is_dir() and entry.name.startswith("char_"):
                    pvt_name = entry.name[5:]
                    try:
                        statuses[pvt_name] = self._determine_status(entry, is_nt=False)
                    except Exception:
                        statuses[pvt_name] = "in_progress"
        
        return statuses
    
    def _aggregate_counts(self, statuses: dict[str, str]) -> dict[str, int]:
        """
        Aggregate PVT status counts.
        
        Args:
            statuses: Dictionary mapping PVT name to status string
            
        Returns:
            Dictionary with counts for passed, failed, in_progress, not_started
        """
        summary = {"passed": 0, "failed": 0, "in_progress": 0, "not_started": 0}
        
        for status in statuses.values():
            if status == "success":
                summary["passed"] += 1
            elif status == "fail":
                summary["failed"] += 1
            elif status == "in_progress":
                summary["in_progress"] += 1
            else:  # idle
                summary["not_started"] += 1
        
        return summary
    
    def execute(self, inp: GetCellPvtStatusInput) -> GetCellPvtStatusOutput:
        """
        Determine PVT status for a given cell.
        
        Args:
            inp: Input containing project, subproject, cell name, cell type, and optional PIC
            
        Returns:
            Output with PVT statuses and summary counts
        """
        # Use PIC's workspace if provided, otherwise use current user's workspace
        if inp.pic:
            base_path = self._resolve_pic_workspace(inp.pic)
        else:
            base_path = PROJECTS_BASE
        
        # Resolve cell directory based on cell type
        if inp.cell_type.lower() == "nt":
            cell_dir = base_path / inp.project / inp.subproject / "design" / "timing" / "nt" / inp.cell
        else:
            cell_dir = base_path / inp.project / inp.subproject / "design" / "timing" / "sis" / inp.cell
        
        is_nt = inp.cell_type.lower() == "nt"
        
        statuses = self._get_statuses_for_cell(cell_dir, is_nt)
        summary = self._aggregate_counts(statuses)
        
        return GetCellPvtStatusOutput(
            cell=inp.cell,
            cell_type=inp.cell_type,
            statuses=statuses,
            summary=summary
        )


__all__ = [
    "ListCells", "ListCellsOutput", 
    "GetNetlistVersion", "GetNetlistVersionInput", "GetNetlistVersionOutput",
    "GetCellPvtStatus", "GetCellPvtStatusInput", "GetCellPvtStatusOutput"
]
