"""P4V integration for QC cells (Phase 1).

Encapsulates querying depot for *_QcPlan.xlsx to discover cell names.
Implements caching similar to legacy qc_service but localized.
"""
from __future__ import annotations
import re
import subprocess
import time
from typing import Optional, Set
from app.domain.qc.repositories import QCP4VRepository
from app.domain.qc.errors import P4VQueryError

P4V_CACHE_CHECK_INTERVAL = 300  # seconds

class QCP4VRepositoryP4(QCP4VRepository):
    def __init__(self) -> None:
        # cache: depot_glob -> {cells:Set[str], last_change:str|None, last_check:float}
        self._cache: dict[str, dict[str, object]] = {}

    def _determine_depot_glob(self, project: str) -> str:
        if project.startswith('h') and len(project) >= 2:
            gen_digit = project[1]
            if gen_digit == '1':
                return "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/qc/*_QcPlan.xlsx"
            if gen_digit == '2':
                return "//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/qc/*_QcPlan.xlsx"
            if gen_digit == '3':
                return "//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/qc/*_QcPlan.xlsx"
        return "//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/qc/*_QcPlan.xlsx"

    def get_last_change(self, depot_glob: str) -> Optional[str]:
        try:
            result = subprocess.run([
                'p4', 'changes', '-m1', '-s', 'submitted', depot_glob.replace('*_QcPlan.xlsx', '...')
            ], capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and result.stdout:
                match = re.match(r'^Change (\d+)', result.stdout)
                if match:
                    return match.group(1)
        except Exception:
            return None
        return None

    def list_cells(self, project: str) -> Set[str]:
        depot_glob = self._determine_depot_glob(project)
        current_time = time.time()
        cache_entry = self._cache.get(depot_glob)
        if cache_entry:
            time_since_check = current_time - (cache_entry.get('last_check') or 0)
            if time_since_check < P4V_CACHE_CHECK_INTERVAL:
                return cache_entry['cells']  # type: ignore
            # check for changes
            last_cached_change = cache_entry.get('last_change')
            current_change = self.get_last_change(depot_glob)
            if current_change and last_cached_change and current_change == last_cached_change:
                cache_entry['last_check'] = current_time
                return cache_entry['cells']  # type: ignore
        cells: Set[str] = set()
        try:
            result = subprocess.run(['p4', 'files', depot_glob], capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    match = re.search(r'/([^/]+)_QcPlan\.xlsx', line)
                    if match and 'delete' not in line.lower():
                        cells.add(match.group(1))
            current_change = self.get_last_change(depot_glob)
            self._cache[depot_glob] = {
                'cells': cells,
                'last_change': current_change,
                'last_check': current_time,
            }
        except Exception as e:
            # fallback to cached cells if available
            if cache_entry:
                cache_entry['last_check'] = current_time
                return cache_entry['cells']  # type: ignore
            raise P4VQueryError(f'Failed to query P4V: {e}')
        return cells

__all__ = ["QCP4VRepositoryP4"]