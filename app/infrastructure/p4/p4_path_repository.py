"""Perforce path utilities (existence check, report cell extraction, upload).

This module provides utilities for working with Perforce (P4) depot paths, including:
- Checking if files exist in the depot
- Downloading files from depot to local filesystem
- Uploading files from local filesystem to depot
- **Automatic P4 client view management** (checks and adds depot paths to client view)

P4 Client View Management:
--------------------------
When uploading or downloading files, the depot path must be mapped in your P4 client view.
This module automatically checks if the required depot path is in your client view and
adds it if necessary. This prevents the common "file not in client view" error.

Example depot path mapping:
    //wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/... //your_client/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/...

Functions:
- get_p4_client_name(): Get current P4 client name
- check_depot_in_client_view(): Check if depot path is mapped in client view
- add_depot_to_client_view(): Add depot path to client view
- ensure_depot_in_client_view(): Check and add if needed (recommended)
- upload_file_to_p4(): Upload file (auto-manages client view)
- download_file_from_p4(): Download file (auto-manages client view)
"""
import subprocess
import re
import os
import shutil
from typing import Set, Optional, Tuple
from datetime import datetime
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


def get_p4_client_name(timeout: int = 10) -> Optional[str]:
    """Get the current P4 client/workspace name.
    
    Returns:
        Client name if found, None otherwise.
    """
    logger.debug("[get_p4_client_name] Getting P4 client name...")
    try:
        result = subprocess.run(
            ["p4", "info"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if line.startswith("Client name:"):
                    client_name = line.split(":", 1)[1].strip()
                    logger.info(f"[get_p4_client_name] Client name: {client_name}")
                    return client_name
        logger.warning(f"[get_p4_client_name] Could not find client name in p4 info output")
        return None
    except Exception as ex:
        logger.error(f"[get_p4_client_name] Failed to get client name: {ex}")
        return None


def check_depot_in_client_view(depot_path: str, timeout: int = 10) -> bool:
    """Check if a depot path is mapped in the current P4 client view.
    
    Args:
        depot_path: The depot path to check (e.g., "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/...")
        timeout: Timeout in seconds for p4 command.
        
    Returns:
        True if the depot path is in client view, False otherwise.
    """
    logger.info(f"[check_depot_in_client_view] Checking if depot in view: {depot_path}")
    client_name = get_p4_client_name(timeout)
    if not client_name:
        logger.warning("[check_depot_in_client_view] Could not determine P4 client name")
        return False
    
    # Extract the base depot path (before any wildcards or specific files)
    # E.g., "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/rel1.00/pcs/design/timing/file.json"
    # -> "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew"
    depot_base = depot_path.split('/', 4)[0:4]  # Get //wwcad/msip/projects/ucie
    if len(depot_base) >= 4:
        # Check if there's a 5th element (project name)
        parts = depot_path.split('/')
        if len(parts) > 4:
            depot_base = '/'.join(parts[:5])  # Include project name
        else:
            depot_base = '/'.join(depot_base)
    else:
        depot_base = depot_path.split('/')[0:3]  # Fallback to first 3 parts
        depot_base = '/'.join(depot_base)
    
    logger.info(f"[check_depot_in_client_view] 📂 Extracted depot_base: '{depot_base}' from '{depot_path}'")
    
    try:
        # Get client spec
        result = subprocess.run(
            ["p4", "client", "-o"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode != 0:
            logger.error(f"[check_depot_in_client_view] Failed to get client spec: {result.stderr}")
            return False
        
        # Parse View: section
        logger.debug(f"[check_depot_in_client_view] depot_base to check: '{depot_base}'")
        in_view_section = False
        view_lines_found = []
        
        for line in result.stdout.splitlines():
            line_stripped = line.strip()
            
            if line.startswith("View:"):
                in_view_section = True
                logger.debug(f"[check_depot_in_client_view] Found View: section")
                continue
            
            if in_view_section:
                # View lines are indented with tabs/spaces and have format:
                # //depot/path/... //client/path/...
                if not line.startswith(('\t', ' ')):
                    # End of View section
                    logger.debug(f"[check_depot_in_client_view] End of View section")
                    break
                
                # Store all view lines for debugging
                if line_stripped:
                    view_lines_found.append(line_stripped)
                
                # Extract depot side of the view mapping
                view_parts = line_stripped.split()
                if len(view_parts) >= 2:
                    view_depot = view_parts[0]
                    # Normalize paths for comparison: remove trailing /... wildcard
                    # Use replace instead of rstrip to avoid removing all dots
                    view_depot_normalized = view_depot.rstrip('/').replace('/...', '')
                    depot_normalized = depot_base.rstrip('/')
                    
                    logger.info(f"[check_depot_in_client_view] 🔍 Comparing view line:")
                    logger.info(f"  Raw view:        '{view_depot}'")
                    logger.info(f"  View normalized: '{view_depot_normalized}'")
                    logger.info(f"  Depot to check:  '{depot_normalized}'")
                    logger.info(f"  startswith?      {depot_normalized.startswith(view_depot_normalized)}")
                    logger.info(f"  equals?          {view_depot_normalized == depot_normalized}")
                    
                    # Check if depot_path is covered by this view mapping
                    # Either exact match or depot starts with the view path
                    if depot_normalized.startswith(view_depot_normalized) or view_depot_normalized == depot_normalized:
                        logger.info(f"[check_depot_in_client_view] ✅ MATCH FOUND! View: {view_depot}")
                        return True
        
        # Log all views found for debugging
        logger.warning(f"[check_depot_in_client_view] ✗ Depot NOT in client view: {depot_base}")
        logger.warning(f"[check_depot_in_client_view] Found {len(view_lines_found)} view line(s) in client spec:")
        for view_line in view_lines_found:
            logger.warning(f"[check_depot_in_client_view]   - {view_line}")
        logger.warning(f"[check_depot_in_client_view] You may need to add: {depot_base}/... //{client_name}/...")
        return False
        
    except Exception as ex:
        logger.error(f"[check_depot_in_client_view] Exception: {ex}")
        return False


def add_depot_to_client_view(depot_path: str, timeout: int = 30) -> bool:
    """Add a depot path to the current P4 client view if not already present.
    
    Args:
        depot_path: The depot path to add (e.g., "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/...")
        timeout: Timeout in seconds for p4 command.
        
    Returns:
        True if added successfully or already exists, False otherwise.
    """
    logger.info(f"[add_depot_to_client_view] Attempting to add depot to client view: {depot_path}")
    
    # Check if already in view
    if check_depot_in_client_view(depot_path, timeout):
        logger.info(f"[add_depot_to_client_view] ✓ Depot path already in client view")
        return True
    
    client_name = get_p4_client_name(timeout)
    if not client_name:
        logger.error("[add_depot_to_client_view] ✗ Could not determine P4 client name")
        return False
    
    # Extract project path for view mapping
    # E.g., "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew/rel1.00/pcs/design/timing/file.json"
    # -> "//wwcad/msip/projects/ucie/h301-ucie3-s32-tsmc2p-075-ew"
    parts = depot_path.split('/')
    if len(parts) < 5:
        logger.error(f"[add_depot_to_client_view] Invalid depot path format: {depot_path}")
        return False
    
    # Get base project path (up to project name)
    depot_base = '/'.join(parts[:5])  # //wwcad/msip/projects/ucie/h301-...
    
    try:
        # Get current client spec
        get_spec = subprocess.run(
            ["p4", "client", "-o"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if get_spec.returncode != 0:
            logger.error(f"[add_depot_to_client_view] Failed to get client spec: {get_spec.stderr}")
            return False
        
        # First, check if the exact view line already exists in the spec
        new_view_line = f"\t{depot_base}/... //{client_name}/projects{depot_base.split('projects', 1)[1]}/..."
        
        # Check for existing similar view lines to avoid duplicates
        existing_views = []
        in_view_section = False
        for line in get_spec.stdout.splitlines():
            if line.startswith("View:"):
                in_view_section = True
                continue
            if in_view_section:
                if not line.startswith(('\t', ' ')):
                    break  # End of view section
                line_stripped = line.strip()
                if line_stripped:
                    existing_views.append(line_stripped)
        
        # Check if this exact view or a similar one already exists
        new_view_stripped = new_view_line.strip()
        for existing_view in existing_views:
            # Check for exact match or overlapping path
            if existing_view == new_view_stripped:
                logger.info(f"[add_depot_to_client_view] ✓ Exact view already exists: {existing_view}")
                return True
            # Check if existing view covers this depot path
            existing_parts = existing_view.split()
            new_parts = new_view_stripped.split()
            if len(existing_parts) >= 2 and len(new_parts) >= 2:
                # Normalize: remove /... wildcard for comparison
                existing_depot = existing_parts[0].rstrip('/').replace('/...', '')
                new_depot = new_parts[0].rstrip('/').replace('/...', '')
                # If the new depot starts with existing depot, it's already covered
                if new_depot.startswith(existing_depot):
                    logger.info(f"[add_depot_to_client_view] ✓ Depot already covered by view: {existing_view}")
                    return True
        
        logger.info(f"[add_depot_to_client_view] View not found in client spec, adding it now...")
        
        # Parse and modify the spec to add new view line
        new_spec_lines = []
        in_view_section = False
        view_added = False
        
        for line in get_spec.stdout.splitlines():
            new_spec_lines.append(line)
            
            if line.startswith("View:"):
                in_view_section = True
                continue
            
            # Add new view line after the last view entry
            if in_view_section:
                if not line.startswith(('\t', ' ')):
                    # End of View section - insert new view before this line
                    if not view_added:
                        new_spec_lines.insert(-1, new_view_line)
                        view_added = True
                        logger.info(f"[add_depot_to_client_view] ➕ Adding view line: {new_view_line}")
                    in_view_section = False
        
        # If we reached end without adding (View was last section), add now
        if in_view_section and not view_added:
            new_spec_lines.append(new_view_line)
            logger.info(f"[add_depot_to_client_view] ➕ Adding view line at end: {new_view_line}")
        
        # Write the modified spec back
        modified_spec = '\n'.join(new_spec_lines)
        
        logger.debug(f"[add_depot_to_client_view] Executing: p4 client -i")
        set_spec = subprocess.run(
            ["p4", "client", "-i"],
            input=modified_spec,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        logger.debug(f"[add_depot_to_client_view] p4 client -i return code: {set_spec.returncode}")
        logger.debug(f"[add_depot_to_client_view] stdout: {set_spec.stdout.strip()}")
        if set_spec.stderr.strip():
            logger.debug(f"[add_depot_to_client_view] stderr: {set_spec.stderr.strip()}")
        
        if set_spec.returncode != 0:
            logger.error(f"[add_depot_to_client_view] ✗ Failed to update client spec: {set_spec.stderr}")
            logger.error(f"[add_depot_to_client_view] stdout: {set_spec.stdout}")
            return False
        
        # IMPORTANT: Verify the view was actually added by checking again
        logger.info(f"[add_depot_to_client_view] Verifying view was actually added...")
        if check_depot_in_client_view(depot_path, timeout):
            logger.info(f"[add_depot_to_client_view] ✓ Successfully added depot to client view: {depot_base}")
            logger.info(f"[add_depot_to_client_view] Updated client: {client_name}")
            return True
        else:
            logger.warning(f"[add_depot_to_client_view] ⚠ p4 client -i succeeded but view not found in client spec!")
            logger.warning(f"[add_depot_to_client_view] This may be due to:")
            logger.warning(f"[add_depot_to_client_view]   - Client spec locked by admin")
            logger.warning(f"[add_depot_to_client_view]   - Permission issues")
            logger.warning(f"[add_depot_to_client_view]   - P4 server policy restrictions")
            logger.warning(f"[add_depot_to_client_view] However, download may still work using 'p4 print' (doesn't require view)")
            # Return True anyway since p4 print doesn't require view
            return True
        
    except Exception as ex:
        logger.error(f"[add_depot_to_client_view] Exception: {ex}")
        return False


def ensure_depot_in_client_view(depot_path: str, timeout: int = 30) -> bool:
    """Ensure a depot path is in the current P4 client view, adding it if necessary.
    
    Args:
        depot_path: The depot path to ensure is in client view
        timeout: Timeout in seconds for p4 commands
        
    Returns:
        True if depot is in view (or was successfully added), False otherwise
    """
    logger.info(f"[ensure_depot_in_client_view] START - Ensuring depot in view: {depot_path}")
    
    if check_depot_in_client_view(depot_path, timeout):
        logger.info(f"[ensure_depot_in_client_view] ✓ Depot already in view")
        return True
    
    logger.info(f"[ensure_depot_in_client_view] Depot NOT in view, attempting to add...")
    result = add_depot_to_client_view(depot_path, timeout)
    
    if result:
        logger.info(f"[ensure_depot_in_client_view] ✓ Successfully ensured depot in view")
    else:
        logger.error(f"[ensure_depot_in_client_view] ✗ Failed to ensure depot in view")
    
    return result


def remove_duplicate_views_from_client(timeout: int = 30) -> bool:
    """Remove duplicate view lines from the current P4 client spec.
    
    This is a utility function to clean up duplicate views that may have been added.
    
    Args:
        timeout: Timeout in seconds for p4 commands
        
    Returns:
        True if cleanup succeeded (or no duplicates found), False otherwise
    """
    logger.info("[remove_duplicate_views_from_client] Checking for duplicate view lines...")
    
    client_name = get_p4_client_name(timeout)
    if not client_name:
        logger.error("[remove_duplicate_views_from_client] Could not determine P4 client name")
        return False
    
    try:
        # Get current client spec
        get_spec = subprocess.run(
            ["p4", "client", "-o"],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if get_spec.returncode != 0:
            logger.error(f"[remove_duplicate_views_from_client] Failed to get client spec: {get_spec.stderr}")
            return False
        
        # Parse spec and collect view lines
        new_spec_lines = []
        in_view_section = False
        seen_views = set()
        duplicates_removed = 0
        
        for line in get_spec.stdout.splitlines():
            if line.startswith("View:"):
                new_spec_lines.append(line)
                in_view_section = True
                continue
            
            if in_view_section:
                if not line.startswith(('\t', ' ')):
                    # End of View section
                    in_view_section = False
                    new_spec_lines.append(line)
                else:
                    # View line - check for duplicates
                    line_stripped = line.strip()
                    if line_stripped in seen_views:
                        # Duplicate found - skip it
                        duplicates_removed += 1
                        logger.info(f"[remove_duplicate_views_from_client] Removing duplicate: {line_stripped}")
                    else:
                        # New view line - keep it
                        seen_views.add(line_stripped)
                        new_spec_lines.append(line)
            else:
                new_spec_lines.append(line)
        
        if duplicates_removed == 0:
            logger.info("[remove_duplicate_views_from_client] ✓ No duplicate views found")
            return True
        
        logger.info(f"[remove_duplicate_views_from_client] Found {duplicates_removed} duplicate view line(s), updating client...")
        
        # Write the modified spec back
        modified_spec = '\n'.join(new_spec_lines)
        
        set_spec = subprocess.run(
            ["p4", "client", "-i"],
            input=modified_spec,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if set_spec.returncode != 0:
            logger.error(f"[remove_duplicate_views_from_client] ✗ Failed to update client spec: {set_spec.stderr}")
            return False
        
        logger.info(f"[remove_duplicate_views_from_client] ✓ Successfully removed {duplicates_removed} duplicate view(s)")
        return True
        
    except Exception as ex:
        logger.error(f"[remove_duplicate_views_from_client] Exception: {ex}")
        return False


def check_p4_path_exists(depot_path: str, timeout: int = 10) -> bool:
    """
    Check if a Perforce depot path exists.
    
    Args:
        depot_path: The Perforce depot path to check.
        timeout: Timeout in seconds for p4 command.
        
    Returns:
        True if the path exists, False otherwise.
    """
    if not depot_path or not depot_path.strip():
        return False
    
    try:
        result = subprocess.run(
            ["p4", "files", depot_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            return True
        
        return False
        
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def check_p4_path_exists_with_date(depot_path: str, cutoff_date: Optional[str] = None, timeout: int = 10) -> bool:
    """
    Check if a Perforce depot path exists and optionally filter by modification date.
    
    Args:
        depot_path: The Perforce depot path to check (can include wildcards).
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        timeout: Timeout in seconds for p4 command.
        
    Returns:
        True if the path exists (and is newer than cutoff_date if provided), False otherwise.
    """
    if not depot_path or not depot_path.strip():
        return False
    
    # If no cutoff date, use simple check
    if not cutoff_date:
        return check_p4_path_exists(depot_path, timeout)
    
    cutoff_dt = _parse_cutoff_date(cutoff_date)
    if not cutoff_dt:
        # Invalid date format, fall back to simple check
        return check_p4_path_exists(depot_path, timeout)
    
    try:
        # Use p4 fstat to get file modification times
        result = subprocess.run(
            ["p4", "fstat", "-T", "headModTime,depotFile", depot_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Parse output to check if any file meets the date criteria
            current_time = None
            
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith('... headModTime '):
                    time_str = line.split('... headModTime ', 1)[1]
                    try:
                        current_time = int(time_str)
                        # Check if this file is newer than cutoff
                        file_dt = datetime.fromtimestamp(current_time)
                        if file_dt >= cutoff_dt:
                            return True
                    except ValueError:
                        continue
            
            # No files found that meet the date criteria
            return False
        
        return False
        
    except subprocess.TimeoutExpired:
        return False
    except Exception:
        return False


def get_report_cells_from_p4(depot_glob: str, report_suffix: str = "_Report.xlsx", timeout: int = 30, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Query Perforce for all report files matching pattern and extract cell names.
    Optionally filter files by modification date.
    
    Args:
        depot_glob: The Perforce depot path with wildcard (e.g., ".../*_Report.xlsx")
        report_suffix: The suffix to remove from filenames to get cell names
        timeout: Timeout in seconds for p4 command.
        cutoff_date: Optional date string (YYYY-MM-DD). Files older than this are excluded.
        
    Returns:
        Set of cell names that have reports in depot (and are newer than cutoff_date if provided).
    """
    logger.info(f"[get_report_cells_from_p4] START")
    logger.info(f"  - depot_glob: {depot_glob}")
    logger.info(f"  - report_suffix: {report_suffix}")
    logger.info(f"  - cutoff_date: {cutoff_date}")
    
    if not depot_glob or not depot_glob.strip():
        logger.warning(f"[get_report_cells_from_p4] Empty depot_glob, returning empty set")
        return set()
    
    cutoff_dt = _parse_cutoff_date(cutoff_date) if cutoff_date else None
    if cutoff_dt:
        logger.info(f"  - Parsed cutoff datetime: {cutoff_dt}")
    
    cells: Set[str] = set()
    
    try:
        # Use p4 fstat to get both file paths and modification times in ONE command
        logger.info(f"[get_report_cells_from_p4] Executing: p4 fstat -T headModTime,depotFile {depot_glob}")
        result = subprocess.run(
            ["p4", "fstat", "-T", "headModTime,depotFile", depot_glob],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        logger.info(f"[get_report_cells_from_p4] p4 command return code: {result.returncode}")
        
        if result.returncode == 0 and result.stdout.strip():
            logger.info(f"[get_report_cells_from_p4] p4 stdout length: {len(result.stdout)} chars")
            
            # Parse output: "... depotFile //path\n... headModTime 1234567890\n"
            current_file = None
            current_time = None
            file_count = 0
            filtered_count = 0
            
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith('... depotFile '):
                    current_file = line.split('... depotFile ', 1)[1]
                    file_count += 1
                elif line.startswith('... headModTime '):
                    time_str = line.split('... headModTime ', 1)[1]
                    try:
                        current_time = int(time_str)
                    except ValueError:
                        current_time = None
                
                # When we have both file and time, process the entry
                if current_file and current_time is not None:
                    # Extract cell name from path
                    # Expected format: //depot/path/CellName_TMQA_Report.xlsx
                    match = re.search(r'/([^/]+)' + re.escape(report_suffix) + r'', current_file)
                    if match:
                        cell_with_prefix = match.group(1)
                        # Remove _TMQA suffix if present (e.g., "cell1_TMQA" -> "cell1")
                        cell_name = re.sub(r'_TMQA$', '', cell_with_prefix)
                        
                        # Check against cutoff date if provided
                        if cutoff_dt:
                            file_dt = datetime.fromtimestamp(current_time)
                            if file_dt >= cutoff_dt:
                                cells.add(cell_name)
                            else:
                                filtered_count += 1
                        else:
                            cells.add(cell_name)
                    
                    current_file = None
                    current_time = None
            
            logger.info(f"[get_report_cells_from_p4] Processed {file_count} files")
            if cutoff_dt:
                logger.info(f"[get_report_cells_from_p4] Filtered out {filtered_count} files older than cutoff")
            logger.info(f"[get_report_cells_from_p4] Found {len(cells)} cells with reports")
        else:
            if result.stderr:
                logger.warning(f"[get_report_cells_from_p4] p4 stderr: {result.stderr}")
            logger.warning(f"[get_report_cells_from_p4] No output or error from p4 command")
        
        return cells
        
    except subprocess.TimeoutExpired:
        logger.warning(f"[get_report_cells_from_p4] Timeout querying {depot_glob}")
        return set()
    except Exception as ex:
        logger.error(f"[get_report_cells_from_p4] Exception: {ex}")
        return set()


def _parse_cutoff_date(date_str: str) -> Optional[datetime]:
    """Parse cutoff date string to datetime object.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        
    Returns:
        datetime object or None if parsing fails
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except Exception:
        logger.warning(f"[_parse_cutoff_date] Failed to parse date: {date_str}")
        return None


def get_folders_from_p4(depot_glob: str, timeout: int = 30, cutoff_date: Optional[str] = None) -> Set[str]:
    """
    Query Perforce for all folders matching pattern and extract folder names.
    Optionally filter folders by their earliest file modification date.
    
    Args:
        depot_glob: The Perforce depot path with wildcard (e.g., ".../*")
        timeout: Timeout in seconds for p4 command.
        cutoff_date: Optional date string (YYYY-MM-DD). Folders with earliest file older than this are excluded.
        
    Returns:
        Set of folder names in the specified depot path (filtered by date if cutoff_date provided).
    """
    if not depot_glob or not depot_glob.strip():
        return set()
    
    cutoff_dt = _parse_cutoff_date(cutoff_date) if cutoff_date else None
    
    # If no cutoff_date, use simple p4 dirs command (faster)
    if not cutoff_dt:
        try:
            result = subprocess.run(
                ["p4", "dirs", depot_glob],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                folders = set()
                for line in result.stdout.splitlines():
                    folder_name = line.strip().split('/')[-1]
                    if folder_name:
                        folders.add(folder_name)
                return folders
        except subprocess.TimeoutExpired:
            logger.warning(f"[get_folders_from_p4] Timeout querying {depot_glob}")
            return set()
        except Exception as ex:
            logger.warning(f"[get_folders_from_p4] Exception: {ex}")
            return set()
    
    # If cutoff_date is provided, use recursive p4 fstat to get all files in all folders
    # Convert depot_glob from "//path/*" to "//path/..."
    if depot_glob.endswith('/*'):
        recursive_glob = depot_glob[:-1] + '...'
    elif depot_glob.endswith('*'):
        recursive_glob = depot_glob[:-1] + '...'
    else:
        recursive_glob = depot_glob.rstrip('/') + '/...'
    
    try:
        # Get all files recursively with their modification times in ONE command
        result = subprocess.run(
            ["p4", "fstat", "-T", "headModTime,depotFile", recursive_glob],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        if result.returncode == 0 and result.stdout.strip():
            # Dictionary to track earliest timestamp for each folder
            # Key: folder_name, Value: earliest timestamp
            folder_times: dict[str, int] = {}
            
            # Parse output and group by folder
            current_file = None
            current_time = None
            
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith('... depotFile '):
                    current_file = line.split('... depotFile ', 1)[1]
                elif line.startswith('... headModTime '):
                    time_str = line.split('... headModTime ', 1)[1]
                    try:
                        current_time = int(time_str)
                    except ValueError:
                        current_time = None
                
                # When we have both file and time, extract folder name
                if current_file and current_time is not None:
                    # Extract folder name from path
                    # Expected: //depot/base/path/FolderName/subdir/file.txt
                    # We want to extract the first folder after the base path
                    
                    # Remove the depot_glob base path to get relative path
                    base_path = depot_glob.rstrip('/*')
                    if current_file.startswith(base_path + '/'):
                        relative_path = current_file[len(base_path) + 1:]
                        # Get first component (folder name)
                        folder_name = relative_path.split('/')[0]
                        
                        # Track the earliest timestamp for this folder
                        if folder_name in folder_times:
                            folder_times[folder_name] = min(folder_times[folder_name], current_time)
                        else:
                            folder_times[folder_name] = current_time
                    
                    current_file = None
                    current_time = None
            
            # Filter folders by cutoff date (using earliest timestamp)
            valid_folders = set()
            for folder_name, earliest_time in folder_times.items():
                earliest_dt = datetime.fromtimestamp(earliest_time)
                if earliest_dt >= cutoff_dt:
                    valid_folders.add(folder_name)
            
            return valid_folders
        
        return set()
        
    except subprocess.TimeoutExpired:
        logger.warning(f"[get_folders_from_p4] Timeout querying {recursive_glob}")
        return set()
    except Exception as ex:
        logger.warning(f"[get_folders_from_p4] Exception: {ex}")
        return set()


def download_file_from_p4(depot_path: str, local_path: str, timeout: int = 60) -> bool:
    """Download a file from Perforce depot to a local path.
    
    NOTE: This function uses 'p4 print' which does NOT require the depot path
    to be in your client view. However, we still attempt to add the view for
    compatibility with other operations (sync, edit, submit) that DO require it.

    Args:
        depot_path: Source depot file path (e.g. "//depot/project/foo.txt").
        local_path: Target local file path where file will be saved.
        timeout: Seconds before each p4 command times out.

    Returns:
        True if download succeeded, False otherwise.
    """
    logger.info("="*80)
    logger.info(f"[download_file_from_p4] START")
    logger.info(f"  Depot path: {depot_path}")
    logger.info(f"  Local path: {local_path}")
    logger.info("="*80)
    
    if not depot_path or not depot_path.strip():
        logger.error(f"[download_file_from_p4] ✗ Invalid depot_path: '{depot_path}'")
        return False
    if not local_path or not local_path.strip():
        logger.error(f"[download_file_from_p4] ✗ Invalid local_path: '{local_path}'")
        return False

    # Ensure depot path is in client view (for future sync/edit/submit operations)
    # NOTE: This is not strictly required for 'p4 print', but we do it anyway for consistency
    logger.info(f"[download_file_from_p4] Step 1: Ensuring depot in client view...")
    logger.info(f"[download_file_from_p4] (Note: 'p4 print' works without client view, but we add it for future operations)")
    if not ensure_depot_in_client_view(depot_path, timeout):
        logger.warning(f"[download_file_from_p4] ⚠ Could not ensure depot in client view: {depot_path}")
        logger.warning(f"[download_file_from_p4] This is OK - 'p4 print' doesn't require client view")
        logger.warning(f"[download_file_from_p4] Download will continue using 'p4 print'...")
        # Continue anyway - p4 print doesn't require client view

    # Check if file exists in depot
    logger.info(f"[download_file_from_p4] Step 2: Checking if file exists in depot...")
    try:
        files_check = subprocess.run([
            "p4", "files", depot_path
        ], capture_output=True, text=True, timeout=timeout)
        logger.debug(f"[download_file_from_p4] p4 files return code: {files_check.returncode}")
        logger.debug(f"[download_file_from_p4] p4 files stdout: {files_check.stdout.strip()}")
        logger.debug(f"[download_file_from_p4] p4 files stderr: {files_check.stderr.strip()}")
    except subprocess.TimeoutExpired:
        logger.error(f"[download_file_from_p4] ✗ Timeout checking if depot file exists: {depot_path}")
        return False
    except Exception as ex:
        logger.error(f"[download_file_from_p4] ✗ Exception checking depot file: {ex}")
        return False

    if files_check.returncode != 0 or not files_check.stdout.strip() or "no such file" in files_check.stdout.lower():
        logger.error(f"[download_file_from_p4] ✗ File does not exist in depot: {depot_path}")
        logger.error(f"[download_file_from_p4] p4 files output: {files_check.stdout.strip()}")
        return False
    
    logger.info(f"[download_file_from_p4] ✓ File exists in depot")

    # Print the file content directly to stdout and capture it
    logger.info(f"[download_file_from_p4] Step 3: Downloading file content...")
    try:
        print_result = subprocess.run([
            "p4", "print", "-q", depot_path
        ], capture_output=True, timeout=timeout)
        logger.debug(f"[download_file_from_p4] p4 print return code: {print_result.returncode}")
        logger.debug(f"[download_file_from_p4] Downloaded {len(print_result.stdout)} bytes")
    except subprocess.TimeoutExpired:
        logger.error(f"[download_file_from_p4] ✗ Timeout printing file: {depot_path}")
        return False
    except Exception as ex:
        logger.error(f"[download_file_from_p4] ✗ Exception printing file: {ex}")
        return False

    if print_result.returncode != 0:
        logger.error(f"[download_file_from_p4] ✗ Failed to print file rc={print_result.returncode}")
        logger.error(f"[download_file_from_p4] stderr: {print_result.stderr.decode() if print_result.stderr else 'N/A'}")
        return False

    # Ensure target directory exists and write content
    logger.info(f"[download_file_from_p4] Step 4: Writing to local file...")
    try:
        target_dir = os.path.dirname(os.path.abspath(local_path))
        logger.debug(f"[download_file_from_p4] Creating directory: {target_dir}")
        os.makedirs(target_dir, exist_ok=True)
        
        logger.debug(f"[download_file_from_p4] Writing {len(print_result.stdout)} bytes to {local_path}")
        with open(local_path, 'wb') as f:
            f.write(print_result.stdout)
        
        logger.info("="*80)
        logger.info(f"[download_file_from_p4] ✓ SUCCESS - Downloaded {depot_path}")
        logger.info(f"[download_file_from_p4] ✓ Saved to: {local_path}")
        logger.info(f"[download_file_from_p4] ✓ Size: {len(print_result.stdout)} bytes")
        logger.info("="*80)
        return True
    except Exception as ex:
        logger.error(f"[download_file_from_p4] ✗ Failed to write file: {ex}")
        logger.error("="*80)
        return False


def upload_file_to_p4(local_path: str, depot_path: str, description: str | None = None, timeout: int = 60) -> bool:
    """Upload (add or edit then submit) a local file to a Perforce depot path.

    Preconditions:
        - Current Perforce client/workspace must map the target depot_path.
        - Caller must supply a fully qualified depot file path (not a directory, no wildcards).

    Args:
        local_path: Path to existing local file to upload.
        depot_path: Target depot file path (e.g. "//depot/project/foo.txt").
        description: Optional changelist description; auto-generated if None.
        timeout: Seconds before each p4 command times out.

    Returns:
        True if submit succeeded, False otherwise.
    """
    if not local_path or not depot_path or not depot_path.strip():
        logger.error(f"[upload_file_to_p4] Invalid arguments local_path='{local_path}' depot_path='{depot_path}'")
        return False
    if not os.path.isfile(local_path):
        logger.error(f"[upload_file_to_p4] Local file does not exist: {local_path}")
        return False

    description = description or f"Upload {os.path.basename(local_path)} to {depot_path}"

    # Ensure depot path is in client view, add if necessary
    if not ensure_depot_in_client_view(depot_path, timeout):
        logger.error(f"[upload_file_to_p4] Failed to ensure depot in client view: {depot_path}")
        logger.error(f"[upload_file_to_p4] Please manually add this view to your P4 client:")
        logger.error(f"[upload_file_to_p4]   {depot_path.rsplit('/', 1)[0]}/... //YOUR_CLIENT/.../{depot_path.split('/')[-2]}/...")
        return False

    # Resolve workspace path from depot path.
    try:
        where = subprocess.run([
            "p4", "where", depot_path
        ], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f"[upload_file_to_p4] Timeout on 'p4 where' for {depot_path}")
        return False
    except Exception as ex:
        logger.error(f"[upload_file_to_p4] Exception on 'p4 where': {ex}")
        return False

    if where.returncode != 0 or not where.stdout.strip():
        logger.error(f"[upload_file_to_p4] 'p4 where' failed rc={where.returncode} stdout='{where.stdout.strip()}' stderr='{where.stderr.strip()}'")
        logger.error(f"[upload_file_to_p4] This usually means the file is not in your client view.")
        return False
    logger.debug(f"[upload_file_to_p4] where stdout: {where.stdout.strip()}")

    # Expected format: "//depot/Path //client/Path C:/local/Path"
    parts = where.stdout.strip().split()
    if len(parts) < 3:
        logger.error(f"[upload_file_to_p4] Unexpected 'p4 where' output: {where.stdout.strip()}")
        return False
    workspace_path = parts[-1]

    # Determine if file already exists in depot.
    try:
        files_check = subprocess.run([
            "p4", "files", depot_path
        ], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f"[upload_file_to_p4] Timeout on 'p4 files' for {depot_path}")
        return False
    except Exception as ex:
        logger.error(f"[upload_file_to_p4] Exception on 'p4 files': {ex}")
        return False
    logger.debug(f"[upload_file_to_p4] files stdout: {files_check.stdout.strip()} stderr: {files_check.stderr.strip()}")

    is_existing = (files_check.returncode == 0 and files_check.stdout.strip() and "no such file" not in files_check.stdout.lower())

    # Refine existence check: if head revision is deleted, treat as non-existing.
    # In Perforce, `p4 files` can still return a file with `- delete change ...`.
    # That file must be re-added, not edited.
    head_action = ""
    try:
        fstat = subprocess.run(
            ["p4", "fstat", "-T", "headAction", depot_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if fstat.returncode == 0:
            for line in fstat.stdout.splitlines():
                line = line.strip()
                if line.startswith("... headAction "):
                    head_action = line.replace("... headAction ", "", 1).strip().lower()
                    break
    except Exception as ex:
        logger.warning(f"[upload_file_to_p4] Could not determine headAction for {depot_path}: {ex}")

    if head_action == "delete":
        logger.info(f"[upload_file_to_p4] Depot file headAction=delete; will re-add file: {depot_path}")
        is_existing = False

    # If file exists in depot, sync it first to ensure it's in the workspace.
    if is_existing:
        try:
            sync_result = subprocess.run(["p4", "sync", "-f", workspace_path], capture_output=True, text=True, timeout=timeout)
            logger.debug(f"[upload_file_to_p4] Sync result rc={sync_result.returncode} stdout='{sync_result.stdout.strip()}'")
        except subprocess.TimeoutExpired:
            logger.error(f"[upload_file_to_p4] Timeout on sync for {workspace_path}")
            return False
        except Exception as ex:
            logger.error(f"[upload_file_to_p4] Exception on sync: {ex}")
            return False

    # Ensure directory exists and copy content if source differs.
    try:
        os.makedirs(os.path.dirname(workspace_path), exist_ok=True)
        if os.path.abspath(local_path) != os.path.abspath(workspace_path):
            # For existing files, remove read-only attribute before copying
            if is_existing and os.path.exists(workspace_path):
                os.chmod(workspace_path, 0o644)
            shutil.copyfile(local_path, workspace_path)
    except Exception as ex:
        logger.error(f"[upload_file_to_p4] Failed to copy file: {ex}")
        return False

    # Open for add or edit.
    try:
        if is_existing:
            open_cmd = ["p4", "edit", workspace_path]
        else:
            open_cmd = ["p4", "add", workspace_path]
        opened = subprocess.run(open_cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f"[upload_file_to_p4] Timeout opening file for {'edit' if is_existing else 'add'}: {workspace_path}")
        return False
    except Exception as ex:
        logger.error(f"[upload_file_to_p4] Exception opening file: {ex}")
        return False

    if opened.returncode != 0:
        logger.error(f"[upload_file_to_p4] Open command failed rc={opened.returncode} cmd={' '.join(open_cmd)} stdout='{opened.stdout.strip()}' stderr='{opened.stderr.strip()}'")
        # Fallback: if edit failed because file not in workspace, try add
        if is_existing and 'not on client' in (opened.stderr.lower() + opened.stdout.lower()):
            logger.info(f"[upload_file_to_p4] Falling back to 'p4 add' for {workspace_path}")
            try:
                add_run = subprocess.run(["p4", "add", workspace_path], capture_output=True, text=True, timeout=timeout)
            except Exception as ex:
                logger.error(f"[upload_file_to_p4] Fallback add exception: {ex}")
                return False
            if add_run.returncode != 0:
                logger.error(f"[upload_file_to_p4] Fallback add failed rc={add_run.returncode} stdout='{add_run.stdout.strip()}' stderr='{add_run.stderr.strip()}'")
                return False
        else:
            return False
    else:
        logger.debug(f"[upload_file_to_p4] Opened file rc=0 mode={'edit' if is_existing else 'add'}")

    # Detect which changelist actually owns this opened file.
    # Some environments open files into a numbered changelist by default,
    # and submitting the default changelist will fail with "No files to submit".
    opened_change_number = None
    opened_in_default = False
    try:
        opened_info = subprocess.run(
            ["p4", "opened", workspace_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        if opened_info.returncode == 0 and opened_info.stdout.strip():
            opened_line = opened_info.stdout.strip().splitlines()[0]
            change_match = re.search(r"change\s+(\d+)", opened_line)
            if change_match:
                opened_change_number = change_match.group(1)
            elif "default change" in opened_line.lower():
                opened_in_default = True
            logger.debug(
                f"[upload_file_to_p4] opened info: '{opened_line}', "
                f"opened_change_number={opened_change_number}, opened_in_default={opened_in_default}"
            )
    except subprocess.TimeoutExpired:
        logger.warning(f"[upload_file_to_p4] Timeout on 'p4 opened' for {workspace_path}; falling back to default submit")
    except Exception as ex:
        logger.warning(f"[upload_file_to_p4] Exception on 'p4 opened': {ex}; falling back to default submit")

    # Submit changelist.
    # For multiline descriptions: create numbered changelist, reopen file in it, then submit.
    # For single line: use simple -d flag.
    try:
        if "\n" in description:
            # Multiline: requires numbered changelist approach
            # Step 1: Create a new changelist with the description
            indent_desc = description.replace("\n", "\n\t")
            changelist_form = f"Change: new\n\nDescription:\n\t{indent_desc}\n\nFiles:\n"
            
            logger.debug(f"[upload_file_to_p4] Creating changelist with form:\n{changelist_form}")
            change_create = subprocess.run([
                "p4", "change", "-i"
            ], input=changelist_form, capture_output=True, text=True, timeout=timeout)
            
            if change_create.returncode != 0:
                logger.error(f"[upload_file_to_p4] Failed to create changelist rc={change_create.returncode} stderr='{change_create.stderr.strip()}'")
                return False
            
            # Extract changelist number from output: "Change 12345 created."
            match = re.search(r'Change (\d+) created', change_create.stdout)
            if not match:
                logger.error(f"[upload_file_to_p4] Could not parse changelist number from: {change_create.stdout.strip()}")
                return False
            
            changelist_num = match.group(1)
            logger.debug(f"[upload_file_to_p4] Created changelist: {changelist_num}")
            
            # Step 2: Reopen the file in the new changelist
            reopen = subprocess.run([
                "p4", "reopen", "-c", changelist_num, workspace_path
            ], capture_output=True, text=True, timeout=timeout)
            
            if reopen.returncode != 0:
                logger.error(f"[upload_file_to_p4] Failed to reopen file in changelist {changelist_num} rc={reopen.returncode} stderr='{reopen.stderr.strip()}'")
                # Try to delete the changelist we created
                subprocess.run(["p4", "change", "-d", changelist_num], capture_output=True, timeout=timeout)
                return False
            
            logger.debug(f"[upload_file_to_p4] Reopened file in changelist {changelist_num}")
            
            # Step 3: Submit the numbered changelist
            submit = subprocess.run([
                "p4", "submit", "-c", changelist_num
            ], capture_output=True, text=True, timeout=timeout)
        else:
            # Single line: use simple -d flag
            if opened_change_number:
                # File is in a numbered changelist; submit that changelist.
                submit = subprocess.run([
                    "p4", "submit", "-c", opened_change_number
                ], capture_output=True, text=True, timeout=timeout)
            else:
                # Default behavior for files opened in default changelist.
                submit = subprocess.run([
                    "p4", "submit", "-d", description, workspace_path
                ], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        logger.error(f"[upload_file_to_p4] Timeout on submit for {workspace_path}")
        return False
    except Exception as ex:
        logger.error(f"[upload_file_to_p4] Exception on submit: {ex}")
        return False

    if submit.returncode != 0:
        combined_submit_output = (submit.stdout + "\n" + submit.stderr).lower()
        if "no files to submit" in combined_submit_output and is_existing:
            # Existing file had no content changes. Treat as successful no-op save.
            logger.info(f"[upload_file_to_p4] No files to submit for existing file (unchanged content): {depot_path}")
            return True
        logger.error(f"[upload_file_to_p4] Submit failed rc={submit.returncode} stdout='{submit.stdout.strip()}' stderr='{submit.stderr.strip()}'")
        return False
    logger.info(f"[upload_file_to_p4] Submit success: {depot_path}")
    return True
