"""
A decorator for a CellRepository that adds file-system based caching.
It stores the results of list_cells in a JSON file.
"""
import json
import os
from pathlib import Path
from typing import List
from app.domain.cell.entities import Cell
from app.domain.cell.repositories import CellRepository
from app.infrastructure.p4.p4_path_repository import upload_file_to_p4, check_p4_path_exists, download_file_from_p4
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class CellRepositoryFileSystemCache(CellRepository):
    """
    A decorator for a CellRepository that adds file-system based caching.
    It stores the results of list_cells in a JSON file.
    """

    def __init__(self, decorated_repo: CellRepository, cache_dir: str = ".cache"):
        self.decorated_repo = decorated_repo
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_path(self, project: str, subproject: str) -> Path:
        """Constructs the path to the cache file."""
        filename = f"project_status_{project}_{subproject}.json"
        return self.cache_dir / filename

    def _get_p4_depot_path(self, project: str, subproject: str) -> str:
        """Constructs the P4 depot path for the cache file."""
        filename = f"project_status_{project}_{subproject}.json"
        return f"//wwcad/msip/projects/ucie/{project}/{subproject}/design/timing/{filename}"

    def list_cells(self, project: str, subproject: str, refresh: bool = False) -> List[Cell]:
        """
        Lists cells, using a file cache.

        Behavior:
        - Normal load (refresh=False): Load from local cache if exists
        - Refresh (refresh=True): Check P4, download if exists, or create new from P4 data
        """
        cache_path = self._get_cache_path(project, subproject)
        depot_path = self._get_p4_depot_path(project, subproject)

        # Normal load: just read local cache if available
        if not refresh and cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    # Filter out config entries (marked with __config__: true)
                    cell_data = [item for item in data if not item.get('__config__')]
                    logger.info(f"[list_cells] Loaded from local cache: {cache_path}")
                    # Build Cell objects while preserving unknown extra fields (e.g., 'hidden')
                    from dataclasses import fields as dc_fields
                    allowed = {fld.name for fld in dc_fields(Cell)}
                    result: List[Cell] = []
                    for item in cell_data:
                        base_kwargs = {k: v for k, v in item.items() if k in allowed}
                        cell_obj = Cell(**base_kwargs)
                        # Attach unknown extras to instance dict
                        extras = {k: v for k, v in item.items() if k not in allowed}
                        if extras:
                            cell_obj.__dict__.update(extras)
                        result.append(cell_obj)
                    return result
            except (json.JSONDecodeError, TypeError) as ex:
                logger.warning(f"[list_cells] Invalid local cache file: {ex}")
                # Fall through to refresh logic

        # Refresh mode: Check P4 first
        if refresh:
            logger.info(f"[list_cells] Refresh mode: checking P4 for {depot_path}")
            
            # Check if file exists in P4
            if check_p4_path_exists(depot_path):
                logger.info(f"[list_cells] File exists in P4, downloading to {cache_path}")
                # Download from P4 to local cache
                if download_file_from_p4(depot_path, str(cache_path)):
                    logger.info(f"[list_cells] Successfully downloaded from P4")
                    try:
                        with open(cache_path, 'r') as f:
                            data = json.load(f)
                            # Filter out config entries (marked with __config__: true)
                            cell_data = [item for item in data if not item.get('__config__')]
                            # Build Cell objects while preserving unknown extra fields (e.g., 'hidden')
                            from dataclasses import fields as dc_fields
                            allowed = {fld.name for fld in dc_fields(Cell)}
                            result: List[Cell] = []
                            for item in cell_data:
                                base_kwargs = {k: v for k, v in item.items() if k in allowed}
                                cell_obj = Cell(**base_kwargs)
                                extras = {k: v for k, v in item.items() if k not in allowed}
                                if extras:
                                    cell_obj.__dict__.update(extras)
                                result.append(cell_obj)
                            return result
                    except (json.JSONDecodeError, TypeError) as ex:
                        logger.error(f"[list_cells] Downloaded file is invalid JSON: {ex}")
                        # Fall through to create new
                else:
                    logger.error(f"[list_cells] Failed to download from P4")
                    # Fall through to create new
            else:
                logger.info(f"[list_cells] File does not exist in P4, will create new")

        # Create new cache file from P4 data
        logger.info(f"[list_cells] Fetching fresh data from P4 and creating cache")
        
        # Load existing cache data to preserve manual edits (if file exists locally)
        existing_cache = {}
        existing_config = None
        if cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    cached_data = json.load(f)
                    # Separate config from cell data
                    for item in cached_data:
                        if item.get('__config__'):
                            existing_config = item
                        elif item.get('ckt_macros'):
                            existing_cache[item['ckt_macros']] = item
                    logger.info(f"[list_cells] Loaded {len(existing_cache)} existing cache entries for merging")
            except (json.JSONDecodeError, TypeError):
                existing_cache = {}

        # Fetch fresh data from P4
        cells = self.decorated_repo.list_cells(project, subproject, refresh=refresh)

        # Merge: P4 data takes precedence for non-None values, but preserve local data otherwise
        merged_cells = []
        for cell in cells:
            cell_name = cell.ckt_macros
            
            # If this cell exists in cache, merge the data
            if cell_name in existing_cache:
                cached_cell = existing_cache[cell_name]
                cell_dict = cell.to_dict()
                
                # For each field, prefer P4 value if not empty/None, otherwise keep cached value
                for key, p4_value in cell_dict.items():
                    cached_value = cached_cell.get(key)
                    
                    # If P4 value is None or empty string, but cache has a value, keep cached value
                    if (p4_value is None or p4_value == "") and cached_value not in (None, ""):
                        cell_dict[key] = cached_value
                
                # Preserve additional fields from cache that don't exist in P4 data (e.g., 'hidden' flag)
                # These will be stored in the cache file but won't be in the Cell object
                cell_extra_fields = {}
                for key, cached_value in cached_cell.items():
                    if key not in cell_dict and cached_value is not None:
                        cell_extra_fields[key] = cached_value
                        logger.debug(f"[list_cells] Preserved cached field '{key}={cached_value}' for cell {cell_name}")
                
                # Create Cell object from known fields
                merged_cell = Cell(**cell_dict)
                # Store extra fields as a dict attribute (hack but works)
                if cell_extra_fields:
                    merged_cell.__dict__.update(cell_extra_fields)
                    logger.info(f"[list_cells] Cell {cell_name} has extra fields: {list(cell_extra_fields.keys())}")
                merged_cells.append(merged_cell)
            else:
                merged_cells.append(cell)

        # Save merged data to cache (preserve config if it existed)
        try:
            with open(cache_path, 'w') as f:
                cache_data = []
                # Add config entry first if it exists
                if existing_config:
                    cache_data.append(existing_config)
                # Add all cell data
                cache_data.extend([cell.to_dict() for cell in merged_cells])
                json.dump(cache_data, f, indent=4)
            logger.info(f"[list_cells] Saved cache to {cache_path}")
        except (IOError, TypeError) as ex:
            logger.error(f"[list_cells] Failed to write cache: {ex}")
            # Failed to write cache, but we can still return the fresh data
            
        return merged_cells

    def update_cell_pic(self, project: str, subproject: str, cell: str, pic: str | None) -> bool:
        """Update PIC value for a cell in the cache file. Returns True if updated. Does NOT upload to P4."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[update_cell_pic] Cache file not found: {cache_path}")
            return False
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            updated = False
            for item in data:
                if item.get('ckt_macros') == cell:
                    item['pic'] = pic or ""
                    updated = True
                    break
            if updated:
                with open(cache_path, 'w') as f:
                    json.dump(data, f, indent=4)
                logger.info(f"[update_cell_pic] PIC updated for cell '{cell}' -> '{pic or ''}'. Saved to {cache_path}")
            return updated
        except Exception as ex:
            logger.error(f"[update_cell_pic] Exception updating PIC for cell '{cell}': {ex}")
            return False

    def batch_update_cell_pic(self, project: str, subproject: str, updates: list[tuple[str, str | None]]) -> int:
        """Batch update PICs for multiple cells. Uploads to P4 only once after all updates."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[batch_update_cell_pic] Cache file not found: {cache_path}")
            return 0
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Build a map for quick lookup
            cell_map = {item.get('ckt_macros'): item for item in data if item.get('ckt_macros')}
            
            updated_count = 0
            for cell, pic in updates:
                if cell in cell_map:
                    cell_map[cell]['pic'] = pic or ""
                    updated_count += 1
                    logger.info(f"[batch_update_cell_pic] Updated cell '{cell}' -> '{pic or ''}'")
            
            if updated_count > 0:
                # Save all changes to local cache
                with open(cache_path, 'w') as f:
                    json.dump(data, f, indent=4)
                logger.info(f"[batch_update_cell_pic] Saved {updated_count} updates to {cache_path}")
                
                # Upload to P4 only ONCE after all updates
                depot_file = self._get_p4_depot_path(project, subproject)
                logger.info(f"[batch_update_cell_pic] Uploading cache file to P4: {depot_file}")
                upload_ok = upload_file_to_p4(str(cache_path), depot_file, description=f"Batch update {updated_count} PIC assignments")
                if upload_ok:
                    logger.info(f"[batch_update_cell_pic] P4 upload success: {depot_file}")
                else:
                    logger.error(f"[batch_update_cell_pic] P4 upload FAILED: {depot_file}")
            
            return updated_count
        except Exception as ex:
            logger.error(f"[batch_update_cell_pic] Exception: {ex}")
            return 0

    def batch_update_cell_fields(self, project: str, subproject: str, updates: list[tuple[str, dict]]) -> int:
        """Batch update arbitrary fields for multiple cells and upload once to P4."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[batch_update_cell_fields] Cache file not found: {cache_path}")
            return 0

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)

            # Build a map for quick lookup
            cell_map = {item.get('ckt_macros'): item for item in data if item.get('ckt_macros')}

            updated_cells = set()
            for cell, values in updates:
                if cell in cell_map and isinstance(values, dict):
                    for k, v in values.items():
                        # Skip updating identifier field
                        if k == 'ckt_macros':
                            continue
                        # JSON should store strings for primitives; keep dicts as-is
                        if isinstance(v, dict):
                            cell_map[cell][k] = v
                        else:
                            cell_map[cell][k] = '' if v is None else str(v)
                    updated_cells.add(cell)

            if updated_cells:
                with open(cache_path, 'w') as f:
                    json.dump(data, f, indent=4)
                logger.info(f"[batch_update_cell_fields] Saved updates for {len(updated_cells)} cell(s) to {cache_path}")

                # Upload once to P4
                depot_file = self._get_p4_depot_path(project, subproject)
                logger.info(f"[batch_update_cell_fields] Uploading cache file to P4: {depot_file}")
                upload_ok = upload_file_to_p4(str(cache_path), depot_file, description=f"Batch update fields for {len(updated_cells)} cells")
                if upload_ok:
                    logger.info("[batch_update_cell_fields] P4 upload success")
                else:
                    logger.error("[batch_update_cell_fields] P4 upload FAILED")

            return len(updated_cells)
        except Exception as ex:
            logger.error(f"[batch_update_cell_fields] Exception: {ex}")
            return 0

    def get_project_config(self, project: str, subproject: str) -> dict:
        """Get project configuration from cache file (returns config dict or empty dict)."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            return {}
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
                # Config is stored as first item if it's a dict with __config__ marker
                if isinstance(data, list) and len(data) > 0:
                    first_item = data[0]
                    if isinstance(first_item, dict) and first_item.get('__config__'):
                        return first_item
            return {}
        except Exception as ex:
            logger.error(f"[get_project_config] Exception: {ex}")
            return {}

    def update_project_config(self, project: str, subproject: str, config_updates: dict) -> bool:
        """Update project configuration and upload to P4."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[update_project_config] Cache file not found: {cache_path}")
            return False
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Find or create config entry (first item with __config__ marker)
            config_entry = None
            config_index = -1
            
            if isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict) and first_item.get('__config__'):
                    config_entry = first_item
                    config_index = 0
            
            if config_entry is None:
                # Create new config entry
                config_entry = {'__config__': True}
                data.insert(0, config_entry)
                config_index = 0
            
            # Update config values
            for key, value in config_updates.items():
                if value is None:
                    # Remove key if value is None
                    config_entry.pop(key, None)
                else:
                    # Set key if value is not None
                    config_entry[key] = value
            
            # Save to local cache
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"[update_project_config] Updated config: {config_updates}")
            
            # Upload to P4
            depot_file = self._get_p4_depot_path(project, subproject)
            upload_ok = upload_file_to_p4(str(cache_path), depot_file, description="Update project configuration")
            
            if upload_ok:
                logger.info(f"[update_project_config] P4 upload success")
            else:
                logger.error(f"[update_project_config] P4 upload FAILED")
            
            return True
        except Exception as ex:
            logger.error(f"[update_project_config] Exception: {ex}")
            return False

    def delete_cell(self, project: str, subproject: str, cell: str) -> bool:
        """Delete a cell from the cache and upload to P4."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[delete_cell] Cache file not found: {cache_path}")
            return False
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Find and remove the cell
            original_count = len(data)
            data = [item for item in data if item.get('ckt_macros') != cell]
            
            if len(data) == original_count:
                logger.warning(f"[delete_cell] Cell '{cell}' not found in cache")
                return False
            
            # Save to local cache
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"[delete_cell] Deleted cell '{cell}' from {cache_path}")
            
            # Upload to P4
            depot_file = self._get_p4_depot_path(project, subproject)
            upload_ok = upload_file_to_p4(str(cache_path), depot_file, description=f"Delete cell {cell}")
            
            if upload_ok:
                logger.info(f"[delete_cell] P4 upload success")
            else:
                logger.error(f"[delete_cell] P4 upload FAILED")
            
            return True
        except Exception as ex:
            logger.error(f"[delete_cell] Exception: {ex}")
            return False

    def batch_delete_cells(self, project: str, subproject: str, cells: list[str]) -> int:
        """Delete multiple cells from the cache and upload to P4 once. Returns number deleted."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[batch_delete_cells] Cache file not found: {cache_path}")
            return 0

        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)

            initial_count = len([item for item in data if item.get('ckt_macros')])

            # Filter out cells to delete
            cells_set = set(cells)
            new_data = [item for item in data if (item.get('ckt_macros') not in cells_set)]

            deleted_count = initial_count - len([item for item in new_data if item.get('ckt_macros')])

            if deleted_count <= 0:
                logger.warning(f"[batch_delete_cells] No matching cells found to delete in cache for {cells}")
                return 0

            # Save updated cache
            with open(cache_path, 'w') as f:
                json.dump(new_data, f, indent=4)
            logger.info(f"[batch_delete_cells] Deleted {deleted_count} cell(s) from {cache_path}")

            # Upload to P4 once
            depot_file = self._get_p4_depot_path(project, subproject)
            logger.info(f"[batch_delete_cells] Uploading cache file to P4: {depot_file}")
            upload_ok = upload_file_to_p4(str(cache_path), depot_file, description=f"Batch delete {deleted_count} cells")
            if upload_ok:
                logger.info(f"[batch_delete_cells] P4 upload success: {depot_file}")
            else:
                logger.error(f"[batch_delete_cells] P4 upload FAILED: {depot_file}")

            return deleted_count
        except Exception as ex:
            logger.error(f"[batch_delete_cells] Exception: {ex}")
            return 0

    def add_cell(self, project: str, subproject: str, cell_data: dict) -> bool:
        """Add a new cell to the cache and upload to P4."""
        cache_path = self._get_cache_path(project, subproject)
        if not cache_path.exists():
            logger.warning(f"[add_cell] Cache file not found: {cache_path}")
            return False
        
        try:
            with open(cache_path, 'r') as f:
                data = json.load(f)
            
            # Check if cell already exists
            cell_name = cell_data.get('ckt_macros')
            if not cell_name:
                logger.error(f"[add_cell] Missing ckt_macros field")
                return False
            
            for item in data:
                if item.get('ckt_macros') == cell_name:
                    logger.warning(f"[add_cell] Cell '{cell_name}' already exists")
                    return False
            
            # Create a new cell from the data
            new_cell = Cell(**cell_data)
            data.append(new_cell.to_dict())
            
            # Save to local cache
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=4)
            logger.info(f"[add_cell] Added cell '{cell_name}' to {cache_path}")
            
            # Upload to P4
            depot_file = self._get_p4_depot_path(project, subproject)
            upload_ok = upload_file_to_p4(str(cache_path), depot_file, description=f"Add cell {cell_name}")
            
            if upload_ok:
                logger.info(f"[add_cell] P4 upload success")
            else:
                logger.error(f"[add_cell] P4 upload FAILED")
            
            return True
        except Exception as ex:
            logger.error(f"[add_cell] Exception: {ex}")
            return False

