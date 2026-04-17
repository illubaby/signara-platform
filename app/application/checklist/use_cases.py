"""Checklist application use cases."""
import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.domain.checklist.entities import Checklist
from app.domain.checklist.template import get_default_checklist_template
from app.infrastructure.logging.logging_config import get_logger
from app.infrastructure.p4.p4_path_repository import (
    check_p4_path_exists, 
    download_file_from_p4, 
    upload_file_to_p4
)

logger = get_logger(__name__)

# Use execution directory cache location (same behavior as project_status)
_CACHE_ROOT = Path(".cache")


class GetChecklist:
    """Use case to get checklist for a project."""
    
    def __init__(self, cache_dir: Path = _CACHE_ROOT):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, project: str) -> Path:
        """Get local cache path for project checklist."""
        project_cache_dir = self.cache_dir / project
        project_cache_dir.mkdir(exist_ok=True)
        return project_cache_dir / "checklists.json"
    
    def _get_p4_depot_path(self, project: str) -> str:
        """Get P4 depot path for project checklist."""
        return f"//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/projects/{project}/checklists.json"
    
    def _get_template_data(self) -> dict:
        """Get default template checklist data."""
        return get_default_checklist_template()
    
    def execute(self, project: str, refresh: bool = False) -> Optional[Checklist]:
        """
        Get checklist for a project.
        
        Args:
            project: Project name
            refresh: If True, download latest from P4. If False, use cache.
            
        Returns:
            Checklist object or None if not found
        """
        logger.info(f"[GetChecklist] Getting checklist for {project}, refresh={refresh}")
        
        cache_path = self._get_cache_path(project)
        depot_path = self._get_p4_depot_path(project)
        
        # Normal load: use local cache if available
        if not refresh and cache_path.exists():
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                logger.info(f"[GetChecklist] Loaded from cache: {cache_path}")
                return Checklist.from_dict(data)
            except (json.JSONDecodeError, TypeError) as ex:
                logger.warning(f"[GetChecklist] Invalid cache file: {ex}")
        
        # Refresh mode: Check P4 first
        if refresh:
            logger.info(f"[GetChecklist] Refresh mode: checking P4 for {depot_path}")
            
            if check_p4_path_exists(depot_path):
                logger.info(f"[GetChecklist] File exists in P4, downloading to {cache_path}")
                if download_file_from_p4(depot_path, str(cache_path)):
                    logger.info(f"[GetChecklist] Successfully downloaded from P4")
                    try:
                        with open(cache_path, 'r') as f:
                            data = json.load(f)
                        return Checklist.from_dict(data)
                    except (json.JSONDecodeError, TypeError) as ex:
                        logger.error(f"[GetChecklist] Downloaded file is invalid JSON: {ex}")
                else:
                    logger.error(f"[GetChecklist] Failed to download from P4")
            else:
                logger.info(f"[GetChecklist] File does not exist in P4")
        
        # If no file exists, create from template
        try:
            data = self._get_template_data()
            logger.info(f"[GetChecklist] Created from default template")
            # Save to cache
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            return Checklist.from_dict(data)
        except Exception as ex:
            logger.error(f"[GetChecklist] Failed to create from template: {ex}")
            return None


class SaveChecklist:
    """Use case to save checklist for a project."""
    
    def __init__(self, cache_dir: Path = _CACHE_ROOT):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_path(self, project: str) -> Path:
        """Get local cache path for project checklist."""
        project_cache_dir = self.cache_dir / project
        project_cache_dir.mkdir(exist_ok=True)
        return project_cache_dir / "checklists.json"
    
    def _get_p4_depot_path(self, project: str) -> str:
        """Get P4 depot path for project checklist."""
        return f"//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/projects/{project}/checklists.json"
    
    def execute(self, project: str, checklist: Checklist) -> bool:
        """
        Save checklist for a project.
        
        Args:
            project: Project name
            checklist: Checklist object to save
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[SaveChecklist] Saving checklist for {project}")
        
        cache_path = self._get_cache_path(project)
        depot_path = self._get_p4_depot_path(project)
        
        try:
            # Save to local cache first
            data = checklist.to_dict()
            with open(cache_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"[SaveChecklist] Saved to cache: {cache_path}")
            
            # Upload to P4
            description = f"Update checklist for {project} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            if upload_file_to_p4(str(cache_path), depot_path, description):
                logger.info(f"[SaveChecklist] Successfully uploaded to P4")
                return True
            else:
                logger.error(f"[SaveChecklist] Failed to upload to P4")
                return False
                
        except Exception as ex:
            logger.error(f"[SaveChecklist] Error: {ex}")
            return False
