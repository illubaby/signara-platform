"""Use case for checking TMQA report status."""
from typing import Set, Optional
from app.infrastructure.p4.p4_path_repository import get_report_cells_from_p4
import logging

logger = logging.getLogger(__name__)

# Cache for TMQA reports: key = "project:subproject:cutoff_date", value = Set[cell_names]
_tmqa_cache: dict[str, Set[str]] = {}
_tmqc_spice_vs_nt_cache: dict[str, Set[str]] = {}
_tmqc_spice_vs_spice_cache: dict[str, Set[str]] = {}
_equalization_cache: dict[str, Set[str]] = {}
_special_check_cache: dict[str, bool] = {}
_package_compare_cache: dict[str, bool] = {}


def clear_report_caches(project: str = None, subproject: str = None):
    """Clear all report status caches. If project/subproject provided, only clear those specific caches."""
    from app.application.cell.final_status import _final_status_cache
    
    global _tmqa_cache, _tmqc_spice_vs_nt_cache, _tmqc_spice_vs_spice_cache
    global _equalization_cache, _special_check_cache, _package_compare_cache
    
    if project and subproject:
        # Clear only caches for specific project/subproject
        logger.info(f"[clear_report_caches] Clearing caches for {project}/{subproject}")
        keys_to_remove = [key for key in _tmqa_cache.keys() if key.startswith(f"{project}:{subproject}:")]
        for key in keys_to_remove:
            _tmqa_cache.pop(key, None)
            _tmqc_spice_vs_nt_cache.pop(key, None)
            _tmqc_spice_vs_spice_cache.pop(key, None)
            _equalization_cache.pop(key, None)
            _special_check_cache.pop(key, None)
            _package_compare_cache.pop(key, None)
        # Also clear final status cache
        final_keys_to_remove = [key for key in _final_status_cache.keys() if key.startswith(f"{project}:{subproject}:")]
        for key in final_keys_to_remove:
            _final_status_cache.pop(key, None)
        logger.info(f"[clear_report_caches] Cleared {len(keys_to_remove)} cache entries + {len(final_keys_to_remove)} final status entries")
    else:
        # Clear all caches
        logger.info("[clear_report_caches] Clearing ALL report caches")
        _tmqa_cache.clear()
        _tmqc_spice_vs_nt_cache.clear()
        _tmqc_spice_vs_spice_cache.clear()
        _equalization_cache.clear()
        _special_check_cache.clear()
        _package_compare_cache.clear()
        _final_status_cache.clear()


def get_tmqa_reports_batch(project: str, subproject: str, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Get all cells with TMQA reports from Perforce (cached).
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        Set of cell names that have TMQA reports (and are newer than cutoff_date if provided).
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    # Return cached result if available
    if cache_key in _tmqa_cache:
        logger.info(f"[get_tmqa_reports_batch] Using CACHED data for {cache_key} - {len(_tmqa_cache[cache_key])} cells")
        return _tmqa_cache[cache_key]
    
    # Query P4 for all TMQA reports
    logger.info(f"[get_tmqa_reports_batch] Cache MISS - querying P4 for {cache_key}")
    depot_glob = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/qa/*_Report.xlsx"
    cells_with_reports = get_report_cells_from_p4(depot_glob, report_suffix="_Report.xlsx", cutoff_date=cutoff_date)
    
    # Cache the result
    _tmqa_cache[cache_key] = cells_with_reports
    logger.info(f"[get_tmqa_reports_batch] Cached result: {len(cells_with_reports)} cells")
    
    return cells_with_reports


def check_tmqa_report_exists(project: str, subproject: str, cell_name: str, cutoff_date: Optional[str] = None) -> bool:
    """
    Check if TMQA report file exists in Perforce (uses batch query with cache).
    
    Args:
        project: Project name
        subproject: Subproject name  
        cell_name: Cell name (ckt_macros)
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are treated as missing.
        
    Returns:
        True if TMQA report exists (status = "Done") and is newer than cutoff_date if provided, False otherwise.
    """
    cells_with_reports = get_tmqa_reports_batch(project, subproject, cutoff_date)
    return cell_name in cells_with_reports


def get_tmqc_spice_vs_nt_reports_batch(project: str, subproject: str, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Get all cells with TMQC Spice vs NT reports from Perforce (cached).
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        Set of cell names that have TMQC Spice vs NT reports (and are newer than cutoff_date if provided).
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    if cache_key in _tmqc_spice_vs_nt_cache:
        return _tmqc_spice_vs_nt_cache[cache_key]
    
    depot_glob = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/qc/*_TMQC_Report.xlsx"
    cells_with_reports = get_report_cells_from_p4(depot_glob, report_suffix="_TMQC_Report.xlsx", cutoff_date=cutoff_date)
    
    _tmqc_spice_vs_nt_cache[cache_key] = cells_with_reports
    return cells_with_reports


def get_tmqc_spice_vs_spice_reports_batch(project: str, subproject: str, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Get all cells with TMQC Spice vs Spice reports from Perforce (cached).
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        Set of cell names that have TMQC Spice vs Spice reports (and are newer than cutoff_date if provided).
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    if cache_key in _tmqc_spice_vs_spice_cache:
        return _tmqc_spice_vs_spice_cache[cache_key]
    
    depot_glob = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/qc/*_TMQCvsReference_Report.xlsx"
    cells_with_reports = get_report_cells_from_p4(depot_glob, report_suffix="_TMQCvsReference_Report.xlsx", cutoff_date=cutoff_date)
    
    _tmqc_spice_vs_spice_cache[cache_key] = cells_with_reports
    return cells_with_reports


def get_equalization_reports_batch(project: str, subproject: str, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Get all cells with Equalization reports from Perforce (cached).
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        Set of cell names that have Equalization reports (and are newer than cutoff_date if provided).
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    if cache_key in _equalization_cache:
        return _equalization_cache[cache_key]
    
    depot_glob = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/qc/*_TMQC_Report_Equalizer.xlsx"
    cells_with_reports = get_report_cells_from_p4(depot_glob, report_suffix="_TMQC_Report_Equalizer.xlsx", cutoff_date=cutoff_date)
    
    _equalization_cache[cache_key] = cells_with_reports
    return cells_with_reports


def check_special_check_exists(project: str, subproject: str, cutoff_date: Optional[str] = None) -> bool:
    """
    Check if Special Check report exists in Perforce (cached).
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        True if SpecialCheckReport.xlsx exists (and is newer than cutoff_date if provided), False otherwise.
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    if cache_key in _special_check_cache:
        return _special_check_cache[cache_key]
    
    depot_path = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/review/SpecialCheckReport.xlsx"
    
    try:
        from app.infrastructure.p4.p4_path_repository import check_p4_path_exists_with_date
        exists = check_p4_path_exists_with_date(depot_path, cutoff_date)
        _special_check_cache[cache_key] = exists
        return exists
    except Exception:
        _special_check_cache[cache_key] = False
        return False


def check_package_compare_exists(project: str, subproject: str, cutoff_date: Optional[str] = None) -> bool:
    """
    Check if Package Compare report exists in Perforce (cached).
    Pattern: PackageCompare_*.xlsx
    
    Args:
        project: Project name
        subproject: Subproject name
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        True if any PackageCompare_*.xlsx file exists (and is newer than cutoff_date if provided), False otherwise.
    """
    cache_key = f"{project}:{subproject}:{cutoff_date or 'none'}"
    
    if cache_key in _package_compare_cache:
        return _package_compare_cache[cache_key]
    
    depot_glob = f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/docs/report/review/PackageCompare_*.xlsx"
    
    try:
        from app.infrastructure.p4.p4_path_repository import check_p4_path_exists_with_date
        exists = check_p4_path_exists_with_date(depot_glob, cutoff_date)
        _package_compare_cache[cache_key] = exists
        return exists
    except Exception:
        _package_compare_cache[cache_key] = False
        return False
