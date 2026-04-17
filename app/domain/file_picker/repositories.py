"""Port (Protocol) for file picker repository.

Defines the contract for file system operations needed by the picker.
"""
from typing import Protocol, List

from .models import PickerEntry, PickerPath


class FilePickerRepository(Protocol):
    """Port for file picker data access operations."""

    def list_directory(self, path: PickerPath) -> List[PickerEntry]:
        """List entries in a directory.
        
        Args:
            path: Directory path to list
            
        Returns:
            List of entries in the directory
            
        Raises:
            PathViolation: If path is invalid
            AccessDenied: If access is denied
        """
        ...

    def validate_path(self, path: PickerPath) -> bool:
        """Validate that a path exists and is accessible.
        
        Args:
            path: Path to validate
            
        Returns:
            True if path is valid and accessible
        """
        ...


__all__ = ["FilePickerRepository"]
