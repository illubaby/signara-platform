"""Filesystem repository for QC testbench and PVT status operations."""
from __future__ import annotations
from pathlib import Path
from typing import List, Optional
from app.domain.qc.entities import PVTRowMeta
from app.domain.qc.repositories import QCTestbenchRepository

class TestbenchRepositoryFS(QCTestbenchRepository):
    def list_testbenches(self, project: str, subproject: str, cell: str) -> List[str]:
        # Support legacy and canonical patterns
        from app.infrastructure.fs.project_root import PROJECTS_BASE
        import re
        
        legacy_root = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'quality' / '4_qc' / f'simulation_{cell}'
        canonical_root = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'quality' / '4_qc' / cell / f'simulations_{cell}'
        names = set()
        for root in (legacy_root, canonical_root):
            if root.exists():
                for p in root.iterdir():
                    if p.is_dir():
                        names.add(p.name)
        
        def extract_testbench_number(name: str) -> int:
            """Extract numeric part from testbench_<number>_* pattern."""
            match = re.match(r'testbench_(\d+)_', name)
            return int(match.group(1)) if match else 999999
        
        # Sort by extracted testbench number, fallback to name for non-matching patterns
        return sorted(names, key=lambda x: (extract_testbench_number(x), x))

    def list_pvts(self, testbench_dir: str) -> List[PVTRowMeta]:
        tb_dir = Path(testbench_dir)
        pvts: List[PVTRowMeta] = []
        if not tb_dir.exists() or not tb_dir.is_dir():
            return pvts
        
        # Valid PVT prefixes (case-insensitive)
        valid_pvt_prefixes = ('ff', 'ss', 'tt', 'sf', 'fs', 'plot')
        
        for child in sorted(tb_dir.iterdir()):
            if not child.is_dir():
                continue
            
            # Check if folder name matches PVT pattern
            name_lower = child.name.lower()
            is_pvt = (
                name_lower == 'plot' or
                any(name_lower.startswith(prefix) for prefix in valid_pvt_prefixes)
            )
            
            if not is_pvt:
                continue
            
            row = self._pvt_status_from_logs(child)
            if row is None:
                pocv_status = self._pocv_status(child)
                pvts.append(PVTRowMeta(
                    pvt=child.name,
                    status='Not Started',
                    log_type=None,
                    log_path=None,
                    pocv_file_status=pocv_status,
                    note='no status files'
                ))
            else:
                pvts.append(row)
        return pvts

    def _pocv_status(self, pvt_dir: Path) -> str:
        # Skip POCV check for "plot" folder
        if pvt_dir.name.lower() == 'plot':
            return 'N/A'
        pocv_file = pvt_dir / 'get_pocv_pbsa_xtalk.txt'
        if not pocv_file.exists():
            return 'Missing'
        try:
            size = pocv_file.stat().st_size
            return 'Empty' if size == 0 else 'Exist'
        except Exception:
            return 'Missing'

    def _pvt_status_from_logs(self, pvt_dir: Path) -> Optional[PVTRowMeta]:
        status_running = pvt_dir / 'statusRunning'
        status_complete = pvt_dir / 'statusComplete'
        pocv_status = self._pocv_status(pvt_dir)
        if not status_running.exists() and not status_complete.exists():
            return PVTRowMeta(
                pvt=pvt_dir.name,
                status='Not Started',
                log_type=None,
                log_path=None,
                pocv_file_status=pocv_status,
                note='no status files'
            )
        for name in ('siliconsmart.log', 'primelib.log'):
            log_path = pvt_dir / name
            if not log_path.exists():
                continue
            status = 'In Progress'
            note = None
            try:
                data = log_path.read_bytes()
                tail = data[-200_000:] if len(data) > 200_000 else data
                text = tail.decode(errors='ignore')
                if any(line.startswith('Error: ') for line in text.splitlines()):
                    status = 'Fail'
                elif 'Shutting down modules' in text:
                    status = 'Passed'
            except Exception as e:
                note = f'read error: {e}'
            return PVTRowMeta(
                pvt=pvt_dir.name,
                status=status,
                log_type=name.split('.')[0],
                log_path=str(log_path),
                pocv_file_status=pocv_status,
                note=note
            )
        return None

__all__ = ["TestbenchRepositoryFS"]