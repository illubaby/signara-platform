"""List Cells Use Case - Architecture-compliant cell listing logic.

This use case orchestrates:
1. Scanning local filesystem for QC cells
2. Querying P4V for additional cells
3. Merging results with cache metadata
4. Returning sorted list of QCCellMeta entities
"""

from typing import List, Dict, Set, Optional, Any, Tuple
import logging
from app.domain.qc.entities import QCCellMeta
from app.infrastructure.qc.cell_repository_fs import QCCellRepositoryFS
from app.infrastructure.qc.p4v_repository import QCP4VRepositoryP4

logger = logging.getLogger(__name__)


class ListCellsUseCase:
    """Use case for listing all QC cells (local + P4V) with metadata."""

    def __init__(
        self,
        cell_repo: QCCellRepositoryFS,
        p4v_repo: QCP4VRepositoryP4,
        cache: Dict[str, Dict[str, Any]]
    ):
        """Initialize with repositories and cache.
        
        Args:
            cell_repo: Filesystem repository for local cell scanning
            p4v_repo: Perforce repository for P4V cell discovery
            cache: Global cache dict for row counts (key: "qc:project:subproject:cell")
        """
        self.cell_repo = cell_repo
        self.p4v_repo = p4v_repo
        self.cache = cache

    def execute(self, project: str, subproject: str) -> List[QCCellMeta]:
        """Execute use case: list all cells with metadata.
        
        Args:
            project: Project name
            subproject: Subproject name
            
        Returns:
            List of QCCellMeta sorted by cell name (reverse), filtered by project characteristics
        """
        # Extract cell-specific cache entries for row counts
        cell_cache = self._extract_cell_cache(project, subproject)
        
        # Scan local filesystem
        local_map = self._scan_local_cells(project, subproject, cell_cache)
        
        # Query P4V for additional cells
        p4v_cells = self._query_p4v_cells(project)
        
        # Merge P4V cells (add cells not found locally)
        for cell_name in p4v_cells:
            if cell_name not in local_map:
                local_map[cell_name] = QCCellMeta(
                    cell=cell_name,
                    has_qcplan=False,
                    has_netlist=False,
                    has_data=False,
                    has_common_source=False,
                    has_ref=False,
                    delay_rows=0,
                    constraint_rows=0,
                )
        
        # Parse project characteristics - check BOTH project and subproject
        # logger.info(f"[QC Cell Filter] ===== FILTER DEBUG START =====")
        # logger.info(f"[QC Cell Filter] Project param: {project}")
        # logger.info(f"[QC Cell Filter] Subproject param: {subproject}")
        
        # Try subproject first, then fallback to project
        project_orientation, project_type = self._parse_project_characteristics(subproject)
        if not project_orientation and not project_type:
            # logger.info(f"[QC Cell Filter] No characteristics in subproject, trying project param...")
            project_orientation, project_type = self._parse_project_characteristics(project)
        
        # logger.info(f"[QC Cell Filter] Detected orientation: {project_orientation}, type: {project_type}")
        # logger.info(f"[QC Cell Filter] Total cells before filter: {len(local_map)}")
        
        # Filter cells based on project characteristics - LOG EACH DECISION
        filtered_cells = []
        for cell in local_map.values():
            should_include = self._should_include_cell(cell.cell, project_orientation, project_type)
            filtered_cells.append(cell) if should_include else None
        
        # logger.info(f"[QC Cell Filter] Total cells after filter: {len(filtered_cells)}")
        # logger.info(f"[QC Cell Filter] ===== FILTER DEBUG END =====")
        
        # Sort (reverse alphabetical per requirement)
        filtered_cells.sort(key=lambda c: c.cell.lower()[::-1])
        
        return filtered_cells

    def _extract_cell_cache(self, project: str, subproject: str) -> Dict[str, Dict]:
        """Extract cell-specific cache entries for row count lookup.
        
        Args:
            project: Project name
            subproject: Subproject name
            
        Returns:
            Dict mapping cell name to cached data (delay/constraint rows)
        """
        prefix = f"qc:{project}:{subproject}:".lower()
        cell_cache = {}
        
        for key, value in self.cache.items():
            if key.startswith(prefix):
                cell_name = key.split(':')[-1]
                cell_cache[cell_name] = value.get("value", {})
        
        return cell_cache

    def _scan_local_cells(
        self,
        project: str,
        subproject: str,
        cell_cache: Dict[str, Dict]
    ) -> Dict[str, QCCellMeta]:
        """Scan local filesystem for cells and enrich with cache data.
        
        Args:
            project: Project name
            subproject: Subproject name
            cell_cache: Cache data for row counts
            
        Returns:
            Dict mapping cell name to QCCellMeta
        """
        items = self.cell_repo.list_local_cells(project, subproject)
        local_map: Dict[str, QCCellMeta] = {}
        
        for meta in items:
            # Enrich with cache data if available
            cached = cell_cache.get(meta.cell)
            if cached:
                meta = QCCellMeta(
                    cell=meta.cell,
                    has_qcplan=meta.has_qcplan,
                    has_netlist=meta.has_netlist,
                    has_data=meta.has_data,
                    has_common_source=meta.has_common_source,
                    has_ref=meta.has_ref,
                    delay_rows=len(cached.get("delay", [])),
                    constraint_rows=len(cached.get("constraint", [])),
                )
            local_map[meta.cell] = meta
        
        return local_map

    def _query_p4v_cells(self, project: str) -> Set[str]:
        """Query P4V for additional cells (silently ignore errors).
        
        Args:
            project: Project name
            
        Returns:
            Set of cell names from P4V (empty if query fails)
        """
        try:
            return self.p4v_repo.list_cells(project)
        except Exception:
            # P4V query failures are non-critical (offline mode)
            return set()

    def _parse_project_characteristics(self, subproject: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse project orientation and connection type from subproject name.
        
        Args:
            subproject: Subproject name (e.g., h215-ucie2-a64c-tsmc3p-12-ns)
            
        Returns:
            Tuple of (orientation, connection_type)
            - orientation: 'ns' (north-south), 'ew' (east-west), or None
            - connection_type: 'a' (advance), 's' (standard), or None
        """
        subproject_lower = subproject.lower()
        
        # Extract orientation from suffix
        orientation = None
        if subproject_lower.endswith('-ns'):
            orientation = 'ns'
        elif subproject_lower.endswith('-ew'):
            orientation = 'ew'
        
        # Extract connection type from third segment (e.g., a64c, s64c)
        parts = subproject.split('-')
        connection_type = None
        if len(parts) >= 3:
            third_part = parts[2].lower()
            if third_part.startswith('a') and 'c' in third_part:
                connection_type = 'a'
            elif third_part.startswith('s') and 'c' in third_part:
                connection_type = 's'
        
        return orientation, connection_type

    def _parse_cell_characteristics(self, cell_name: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse cell orientation and connection type from cell name.
        
        Args:
            cell_name: Cell name (e.g., dwc_ucie2phy_rx16b_a_ns, dwc_ucie2phy_lcdl_ns)
            
        Returns:
            Tuple of (orientation, connection_type)
            - orientation: 'ns', 'ew', or None (no orientation suffix)
            - connection_type: 'a' (advance), 's' (standard), or None (common cell)
        """
        cell_lower = cell_name.lower()
        
        # Extract orientation from suffix
        orientation = None
        if cell_lower.endswith('_ns'):
            orientation = 'ns'
        elif cell_lower.endswith('_ew'):
            orientation = 'ew'
        
        # Extract connection type (must be right before orientation or at end)
        connection_type = None
        if orientation:
            # Check for _a_ns, _a_ew, _s_ns, _s_ew patterns
            if cell_lower.endswith(f'_a_{orientation}'):
                connection_type = 'a'
            elif cell_lower.endswith(f'_s_{orientation}'):
                connection_type = 's'
        
        return orientation, connection_type

    def _should_include_cell(
        self,
        cell_name: str,
        project_orientation: Optional[str],
        project_type: Optional[str]
    ) -> bool:
        """Determine if a cell should be included based on project characteristics.
        
        Rules:
        1. Orientation filter: Exclude cells with mismatched orientation
           - Project ns: exclude cells with ew suffix
           - Project ew: exclude cells with ns suffix
        2. Connection type filter: Exclude cells with mismatched type
           - Project advance: exclude standard cells (but include common cells)
           - Project standard: exclude advance cells (but include common cells)
        3. Common cells (no orientation or no type suffix) are always included
        
        Args:
            cell_name: Cell name to check
            project_orientation: Project orientation ('ns', 'ew', or None)
            project_type: Project connection type ('a', 's', or None)
            
        Returns:
            True if cell should be included, False otherwise
        """
        cell_orientation, cell_type = self._parse_cell_characteristics(cell_name)
        # logger.info(f"[QC Cell Filter]   Cell: {cell_name} -> orientation={cell_orientation}, type={cell_type}")
        
        # Rule 1: Orientation filter
        if project_orientation and cell_orientation:
            if project_orientation != cell_orientation:
                # logger.info(f"[QC Cell Filter]   ❌ EXCLUDE: orientation mismatch (need {project_orientation}, got {cell_orientation})")
                return False
        
        # Rule 2: Connection type filter
        if project_type and cell_type:
            if project_type != cell_type:
                # logger.info(f"[QC Cell Filter]   ❌ EXCLUDE: type mismatch (need {project_type}, got {cell_type})")
                return False
        
        # All other cases: include (common cells, no conflicts)
        # logger.info(f"[QC Cell Filter]   ✅ INCLUDE")
        return True
