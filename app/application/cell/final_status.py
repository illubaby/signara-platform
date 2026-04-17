"""Use case for checking final release status based on raw_lib folder existence."""
from typing import Set, Optional
from app.infrastructure.p4.p4_path_repository import get_folders_from_p4

# Cache for final status: key = "project:subproject:custom_path:cutoff_date", value = Set[cell_names]
_final_status_cache: dict[str, Set[str]] = {}


def get_final_status_cells_batch(project: str, subproject: str, custom_path: str = None, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Get all cells with final release status from Perforce (cached).
    
    Checks for cell folder existence in:
    //wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/release/internal/raw_lib/{cell_name}/
    
    Args:
        project: Project name
        subproject: Subproject name
        custom_path: Optional custom depot path (supports {project} and {subproject} placeholders)
        cutoff_date: Optional date string (YYYY-MM-DD). Folders with all files older than this are excluded.
        
    Returns:
        Set of cell names that have raw_lib folders (final release complete) and are newer than cutoff_date if provided.
    """
    # Build cache key including custom path and cutoff_date if provided
    cache_key = f"{project}:{subproject}:{custom_path or 'default'}:{cutoff_date or 'none'}"
    
    # Return cached result if available
    if cache_key in _final_status_cache:
        return _final_status_cache[cache_key]
    
    # Use custom path if provided, otherwise use default
    if custom_path:
        depot_path = custom_path.replace('{project}', project).replace('{subproject}', subproject)
        # Auto-append * if missing (common user mistake)
        if not depot_path.endswith('*'):
            depot_path = depot_path.rstrip('/') + '/*'
    else:
        depot_path = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/release/internal/raw_lib/*"
    
    cells_with_raw_lib = get_folders_from_p4(depot_path, cutoff_date=cutoff_date)
    
    # Cache the result
    _final_status_cache[cache_key] = cells_with_raw_lib
    
    return cells_with_raw_lib


def check_final_status_exists(project: str, subproject: str, cell_name: str) -> bool:
    """
    Check if cell has final release status (raw_lib folder exists) in Perforce.
    
    Args:
        project: Project name
        subproject: Subproject name  
        cell_name: Cell name (ckt_macros)
        
    Returns:
        True if raw_lib folder exists (final status complete), False otherwise.
    """
    cells_with_raw_lib = get_final_status_cells_batch(project, subproject)
    return cell_name in cells_with_raw_lib
