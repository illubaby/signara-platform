"""Filesystem implementation of PvtStatusRepository (Phase 4).

Provides granular PVT status classification and aggregation for a cell.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from app.domain.saf.repositories import PvtStatusRepository

class PvtStatusRepositoryFS(PvtStatusRepository):
    MAX_LOG_BYTES = 2_000_000

    def _determine(self, pvt_dir: Path, is_nt: bool = False) -> str:
        """Determine PVT status for SiS or NT cells.
        
        Args:
            pvt_dir: Path to PVT directory (char_<PVT> for SiS, <PVT> for NT)
            is_nt: True if this is an NT cell, False for SiS cell
            
        Returns:
            Status string: "success", "fail", "in_progress", or "idle"
        """
        if is_nt:
            # NT cell: check ScratchDir/timing/<PVT>/timing.log
            timing_log = pvt_dir / "timing.log"
            
            import logging
            logger = logging.getLogger(__name__)

            
            if not timing_log.exists():
                return "idle"  # Not Started
            
            # Check for "Diagnostics summary:" line
            found_diagnostics_line = False
            has_error = False
            line_count = 0
            last_lines = []
            
            try:
                with timing_log.open("r", errors="ignore") as fh:
                    for line in fh:
                        line_count += 1
                        # Keep last 3 lines for debugging
                        last_lines.append(line.strip())
                        if len(last_lines) > 3:
                            last_lines.pop(0)
                        
                        if "Diagnostics summary:" in line:
                            found_diagnostics_line = True
                            # Check if there's "error" in this line (case-insensitive)
                            if "error" in line.lower():
                                has_error = True
                            break
                
                if not found_diagnostics_line:
                    logger.info(f"[NT PVT Status] Scanned {line_count} lines, no 'Diagnostics summary:' found")
                    logger.info(f"[NT PVT Status] Last 3 lines: {last_lines}")
                        
            except Exception as e:
                logger.error(f"[NT PVT Status] Exception reading file: {e}")
                return "in_progress"
            
            if not found_diagnostics_line:
                return "in_progress"  # File exists but no "Diagnostics summary:" yet
            
            if has_error:
                return "fail"  # Has error at "Diagnostics summary:" line
            else:
                return "success"  # No error at "Diagnostics summary:" line
        else:
            # SiS cell: existing logic
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
                            if stripped.startswith("Error ") or stripped.startswith("Error:") or stripped.startswith("ERROR ") or stripped.startswith("ERROR:"):
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

    def statuses_for_cell(self, cell_dir: str, is_nt: bool = False) -> Dict[str, str]:
        """Get PVT statuses for a cell.
        
        Args:
            cell_dir: Path to cell directory
            is_nt: True if this is an NT cell, False for SiS cell
            
        Returns:
            Dictionary mapping PVT name to status string
        """
        path = Path(cell_dir)
        statuses: Dict[str, str] = {}
        if not path.exists() or not path.is_dir():
            return statuses
        
        if is_nt:
            # NT cell: check ScratchDir/timing/<PVT>/ directories
            # Directory names are like: Run_<pvt>_etm_<number>
            # But pvt_corners.lst contains just: <pvt>
            # So we need to map directory names back to base PVT names
            import logging
            logger = logging.getLogger(__name__)
            scratch_timing = path / "ScratchDir" / "timing"
            
            if not scratch_timing.exists() or not scratch_timing.is_dir():
                logger.warning(f"[NT statuses_for_cell] Path does not exist or not a directory")
                return statuses
            
            # Build a mapping from base PVT names to their status
            # Directory format: Run_<base_pvt_name>_etm_<number>
            for entry in scratch_timing.iterdir():
                if entry.is_dir():
                    dir_name = entry.name
                    
                    # Extract base PVT name by removing Run_ prefix and _etm_<number> suffix
                    base_pvt_name = dir_name
                    if base_pvt_name.startswith("Run_"):
                        base_pvt_name = base_pvt_name[4:]  # Remove "Run_"
                    # Remove _etm_<number> suffix
                    if "_etm_" in base_pvt_name:
                        base_pvt_name = base_pvt_name.rsplit("_etm_", 1)[0]
                    
                    
                    try:
                        status = self._determine(entry, is_nt=True)
                        # Store with base name, prioritize success/fail over idle
                        if base_pvt_name not in statuses or status in ('success', 'fail', 'in_progress'):
                            statuses[base_pvt_name] = status
                    except Exception as e:
                        logger.error(f"[NT statuses_for_cell] Exception for {dir_name}: {e}")
                        if base_pvt_name not in statuses:
                            statuses[base_pvt_name] = "in_progress"
            
        else:
            # SiS cell: check char_<PVT> directories
            for entry in path.iterdir():
                if entry.is_dir() and entry.name.startswith("char_"):
                    pvt_name = entry.name[5:]
                    try:
                        statuses[pvt_name] = self._determine(entry, is_nt=False)
                    except Exception:
                        statuses[pvt_name] = "in_progress"
        
        return statuses

    def aggregate_counts(self, cell_dir: str, is_nt: bool = False) -> Dict[str, int]:
        """Aggregate PVT status counts for a cell.
        
        Args:
            cell_dir: Path to cell directory
            is_nt: True if this is an NT cell, False for SiS cell
            
        Returns:
            Dictionary with counts for passed, failed, in_progress, not_started
        """
        summary = {"passed": 0, "failed": 0, "in_progress": 0, "not_started": 0}
        path = Path(cell_dir)
        if not path.exists() or not path.is_dir():
            return summary
        
        if is_nt:
            # NT cell: aggregate from ScratchDir/timing/<PVT>/ directories
            scratch_timing = path / "ScratchDir" / "timing"
            if not scratch_timing.exists() or not scratch_timing.is_dir():
                return summary
            
            for entry in scratch_timing.iterdir():
                if entry.is_dir():
                    status = self._determine(entry, is_nt=True)
                    if status == "success":
                        summary["passed"] += 1
                    elif status == "fail":
                        summary["failed"] += 1
                    elif status == "in_progress":
                        summary["in_progress"] += 1
                    else:
                        summary["not_started"] += 1
        else:
            # SiS cell: aggregate from char_<PVT> directories
            for entry in path.iterdir():
                if entry.is_dir() and entry.name.startswith("char_"):
                    status = self._determine(entry, is_nt=False)
                    if status == "success":
                        summary["passed"] += 1
                    elif status == "fail":
                        summary["failed"] += 1
                    elif status == "in_progress":
                        summary["in_progress"] += 1
                    else:
                        summary["not_started"] += 1
        
        return summary

__all__ = ["PvtStatusRepositoryFS"]
