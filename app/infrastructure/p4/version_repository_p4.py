"""P4-based version repository implementation."""
import subprocess
import re
from typing import Optional, Tuple
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


class VersionRepositoryP4:
    """Fetch version from Perforce depot."""
    
    def get_remote_version_info(self, depot_path: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
        """Fetch __version__ and __version_deadline__ from remote __init__.py in P4 depot.
        
        Args:
            depot_path: P4 depot path to the __init__.py file
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (version, deadline) - both can be None if not found
        """
        logger.debug(f"[get_remote_version_info] Fetching version info from: {depot_path}")
        try:
            result = subprocess.run(
                ["p4", "print", "-q", depot_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.warning(f"[get_remote_version_info] p4 print failed: {result.stderr}")
                return None, None
            
            content = result.stdout
            if not content:
                logger.warning(f"[get_remote_version_info] Empty response from p4 print")
                return None, None
            
            # Parse __version__ = "x.y.z" from the file content
            version = None
            version_match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
            if version_match:
                version = version_match.group(1)
                logger.info(f"[get_remote_version_info] Found remote version: {version}")
            else:
                logger.warning(f"[get_remote_version_info] Could not find __version__ in file")
            
            # Parse __version_deadline__ = "YYYY-MM-DD" from the file content
            deadline = None
            deadline_match = re.search(r'__version_deadline__\s*=\s*["\']([^"\']+)["\']', content)
            if deadline_match:
                deadline = deadline_match.group(1)
                logger.info(f"[get_remote_version_info] Found remote deadline: {deadline}")
            else:
                logger.debug(f"[get_remote_version_info] No __version_deadline__ found in file")
            
            return version, deadline
            
        except subprocess.TimeoutExpired:
            logger.error(f"[get_remote_version_info] Timeout fetching from P4")
            return None, None
        except Exception as ex:
            logger.error(f"[get_remote_version_info] Error: {ex}")
            return None, None
    
    def get_remote_version(self, depot_path: str, timeout: int = 30) -> Optional[str]:
        """Fetch __version__ from remote __init__.py in P4 depot.
        
        Args:
            depot_path: P4 depot path to the __init__.py file
            timeout: Command timeout in seconds
            
        Returns:
            Version string if found, None otherwise
        """
        version, _ = self.get_remote_version_info(depot_path, timeout)
        return version

    def get_remote_changelog(self, depot_path: str, version: str, timeout: int = 30) -> Optional[str]:
        """Fetch changelog for a specific version from remote CHANGELOG.md in P4 depot.
        
        Args:
            depot_path: P4 depot path to the __init__.py file (will derive changelog path)
            version: Version to extract from changelog
            timeout: Command timeout in seconds
            
        Returns:
            Changelog content for the specified version, or None if not found
        """
        # Derive changelog path from __init__.py path
        # //wwcad/.../app/__init__.py -> //wwcad/.../app/changelog/CHANGELOG.md
        changelog_path = depot_path.replace("__init__.py", "changelog/CHANGELOG.md")
        logger.debug(f"[get_remote_changelog] Fetching changelog from: {changelog_path}")
        
        try:
            result = subprocess.run(
                ["p4", "print", "-q", changelog_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout
            )
            
            if result.returncode != 0:
                logger.warning(f"[get_remote_changelog] p4 print failed: {result.stderr}")
                return None
            
            content = result.stdout
            if not content:
                logger.warning(f"[get_remote_changelog] Empty response from p4 print")
                return None
            
            # Extract section for the specific version
            pattern = rf"(## v?{re.escape(version)}.*?)(?=\n## |\n---|\Z)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                changelog = match.group(1).strip()
                logger.info(f"[get_remote_changelog] Found changelog for v{version}")
                return changelog
            else:
                logger.warning(f"[get_remote_changelog] No changelog section found for v{version}")
                return None
            
        except subprocess.TimeoutExpired:
            logger.error(f"[get_remote_changelog] Timeout fetching from P4")
            return None
        except Exception as ex:
            logger.error(f"[get_remote_changelog] Error: {ex}")
            return None
