"""Infrastructure adapter: FileDownloadRepository FS implementation.

Validates file paths for download exposure. Keeps logic minimal; any future
security (root whitelists, quarantine) can be added here without changing
use cases or routers.
"""
from pathlib import Path
import os
import logging

from app.domain.file_operations.repositories import FileDownloadRepository

logger = logging.getLogger(__name__)

class FileDownloadRepositoryFS(FileDownloadRepository):
    """Filesystem implementation of FileDownloadRepository."""

    def validate_for_download(self, file_path: Path) -> Path:  # pragma: no cover (covered via use case tests)
        # Resolve to absolute path
        resolved = file_path.expanduser().resolve()
        logger.debug(f"Validating file for download: {resolved}")

        if not resolved.exists():
            logger.warning(f"Download request - file not found: {resolved}")
            raise FileNotFoundError(f"File not found: {resolved}")
        if not resolved.is_file():
            logger.warning(f"Download request - not a regular file: {resolved}")
            raise ValueError(f"Path is not a file: {resolved}")
        # Basic readability check
        if not os.access(resolved, os.R_OK):
            logger.error(f"Download request - unreadable file: {resolved}")
            raise PermissionError(f"File not readable: {resolved}")
        return resolved

__all__ = ["FileDownloadRepositoryFS"]
