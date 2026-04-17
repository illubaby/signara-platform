"""File picker application layer use cases.

Orchestrates file picking operations without HTTP or infrastructure knowledge.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from app.domain.file_picker.models import PickerPath, PickerEntry
from app.domain.file_picker.repositories import FilePickerRepository
from app.domain.file_picker.errors import PathViolation


# -------------------- DTOs --------------------
@dataclass(frozen=True)
class BrowseDirectoryInput:
    """Input for browsing a directory."""
    path: str


@dataclass(frozen=True)
class BrowseDirectoryOutput:
    """Output containing directory entries."""
    current_path: str
    parent_path: str
    entries: List[PickerEntry]


@dataclass(frozen=True)
class ValidatePathInput:
    """Input for path validation."""
    path: str


@dataclass(frozen=True)
class ValidatePathOutput:
    """Output of path validation."""
    is_valid: bool
    is_directory: bool
    error_message: str = ""


# -------------------- Use Cases --------------------
class BrowseDirectory:
    """Use case for browsing directories in the file picker."""

    def __init__(self, repo: FilePickerRepository):
        self.repo = repo

    def execute(self, inp: BrowseDirectoryInput) -> BrowseDirectoryOutput:
        """Browse a directory and return its contents.
        
        Args:
            inp: Input containing the path to browse
            
        Returns:
            Output containing current path, parent path, and entries
            
        Raises:
            PathViolation: If path is invalid
        """
        picker_path = PickerPath(inp.path)
        entries = self.repo.list_directory(picker_path)
        
        # Sort: directories first, then files, both alphabetically
        sorted_entries = sorted(entries, key=lambda e: (not e.is_dir, e.name.lower()))
        
        # Determine parent path
        path_obj = picker_path.as_path()
        parent_path = str(path_obj.parent) if path_obj.parent != path_obj else ""
        
        return BrowseDirectoryOutput(
            current_path=inp.path,
            parent_path=parent_path,
            entries=sorted_entries
        )


class ValidatePath:
    """Use case for validating a file/folder path."""

    def __init__(self, repo: FilePickerRepository):
        self.repo = repo

    def execute(self, inp: ValidatePathInput) -> ValidatePathOutput:
        """Validate if a path exists and is accessible.
        
        Args:
            inp: Input containing the path to validate
            
        Returns:
            Output indicating validation result
        """
        try:
            picker_path = PickerPath(inp.path)
            is_valid = self.repo.validate_path(picker_path)
            
            if not is_valid:
                return ValidatePathOutput(
                    is_valid=False,
                    is_directory=False,
                    error_message="Path does not exist or is not accessible"
                )
            
            # Check if it's a directory
            path_obj = picker_path.as_path()
            is_directory = path_obj.is_dir()
            
            return ValidatePathOutput(
                is_valid=True,
                is_directory=is_directory
            )
        except PathViolation as e:
            return ValidatePathOutput(
                is_valid=False,
                is_directory=False,
                error_message=str(e)
            )


__all__ = [
    "BrowseDirectory",
    "ValidatePath",
    "BrowseDirectoryInput",
    "BrowseDirectoryOutput",
    "ValidatePathInput",
    "ValidatePathOutput",
]
