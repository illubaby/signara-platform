"""Domain models for file/folder picker feature.

Pure business concepts for browsing and selecting files/folders.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from .errors import PathViolation


@dataclass(frozen=True)
class PickerPath:
    """Value object representing a path in the picker."""
    value: str

    def __post_init__(self):
        if not self.value:
            raise PathViolation("Path cannot be empty")

    def as_path(self) -> Path:
        return Path(self.value)

    def is_absolute(self) -> bool:
        return Path(self.value).is_absolute()


@dataclass(frozen=True)
class PickerEntry:
    """Represents a file or folder entry in the picker."""
    name: str
    path: str
    is_dir: bool
    is_symlink: bool = False
    size: Optional[int] = None
    modified_time: Optional[str] = None


@dataclass(frozen=True)
class PickerResult:
    """Result of a picker selection."""
    selected_path: str
    is_directory: bool


__all__ = [
    "PickerPath",
    "PickerEntry",
    "PickerResult",
]
