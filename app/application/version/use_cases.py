"""Version check use cases."""
from datetime import datetime
from typing import Optional
from app.domain.version import VersionInfo, VersionRepository
from app import __version__, __version_depot_path__
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class CheckVersion:
    """Use case for checking application version against remote depot."""
    
    def __init__(self, repo: VersionRepository):
        self.repo = repo
    
    def execute(self) -> VersionInfo:
        """Check local version against remote P4 version.
        
        Deadline is fetched from P4 remote, not local - this ensures
        the admin controls when users must update.
        
        Returns:
            VersionInfo with comparison results
        """
        local_version = __version__
        depot_path = __version_depot_path__
        
        # Fetch remote version AND deadline from P4
        remote_version, remote_deadline_str = self.repo.get_remote_version_info(depot_path)
        
        # Parse deadline from remote
        deadline: Optional[datetime] = None
        if remote_deadline_str:
            try:
                deadline = datetime.strptime(remote_deadline_str, "%Y-%m-%d")
                # Set to end of day
                deadline = deadline.replace(hour=23, minute=59, second=59)
            except ValueError:
                logger.warning(f"[CheckVersion] Invalid remote deadline format: {remote_deadline_str}")
        
        logger.info(
            f"[CheckVersion] Local: {local_version}, Remote: {remote_version}, "
            f"Deadline: {deadline}, Outdated: {local_version != remote_version if remote_version else 'N/A'}"
        )
        
        return VersionInfo(
            local_version=local_version,
            remote_version=remote_version,
            deadline=deadline
        )
