"""Version repository protocol."""
from typing import Protocol, Optional, Tuple


class VersionRepository(Protocol):
    """Protocol for fetching version from remote source."""
    
    def get_remote_version(self, depot_path: str) -> Optional[str]:
        """Fetch the version string from remote depot.
        
        Args:
            depot_path: P4 depot path to the __init__.py file
            
        Returns:
            Version string if found, None otherwise
        """
        ...
    
    def get_remote_version_info(self, depot_path: str) -> Tuple[Optional[str], Optional[str]]:
        """Fetch version and deadline from remote depot.
        
        Args:
            depot_path: P4 depot path to the __init__.py file
            
        Returns:
            Tuple of (version, deadline) - both can be None if not found
        """
        ...
