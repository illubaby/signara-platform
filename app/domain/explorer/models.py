"""Domain models & value objects for the Explorer feature.

Pure business concepts: no FastAPI, no pandas, no filesystem side-effects.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional

from .errors import PathViolation

# -------------------- Value Objects --------------------
@dataclass(frozen=True)
class RelativePath:
    value: str

    def __post_init__(self):
        if self.value in ("", "."):
            object.__setattr__(self, "value", "")  # normalize root
        if Path(self.value).is_absolute():
            raise PathViolation("Absolute paths not allowed")
        parts = [p for p in self.value.split('/') if p not in ('', '.')]
        if any(p == '..' for p in parts):
            raise PathViolation("Parent traversal '..' not allowed")

    def as_parts(self) -> List[str]:
        return [p for p in self.value.split('/') if p]

    def is_root(self) -> bool:
        return self.value == ""

# -------------------- Core Models --------------------
@dataclass(frozen=True)
class ExplorerRoot:
    path: Path

    def __post_init__(self):
        if not self.path.is_absolute():
            raise PathViolation("Root must be absolute")
        if not self.path.exists():
            raise PathViolation(f"Root does not exist: {self.path}")
        if not self.path.is_dir():
            raise PathViolation(f"Root is not a directory: {self.path}")

@dataclass(frozen=True)
class FileEntry:
    name: str
    is_dir: bool
    is_symlink: bool
    external: bool
    size: Optional[int] = None

@dataclass(frozen=True)
class ExcelSheet:
    name: str
    columns: List[str]
    rows: List[List[str]]
    row_count: int
    truncated: bool = False
    error: Optional[str] = None

@dataclass(frozen=True)
class ExcelWorkbook:
    sheets: Dict[str, ExcelSheet]
    sheet_names: List[str]
    truncated: bool

@dataclass(frozen=True)
class FileContent:
    relative: RelativePath
    name: str
    size: int
    is_text: bool
    truncated: bool
    content: Optional[str]
    excel: Optional[ExcelWorkbook] = None

@dataclass(frozen=True)
class WriteResult:
    name: str
    bytes_written: int
    created: bool

# -------------------- Policies --------------------
@dataclass(frozen=True)
class ExtensionPolicy:
    allowed: List[str]
    blocked: List[str]

    def is_allowed(self, ext: str) -> bool:
        e = ext.lower()
        if e in (b.lower() for b in self.blocked):
            return False
        return e in (a.lower() for a in self.allowed)

@dataclass(frozen=True)
class SizeLimitPolicy:
    max_read_bytes: int
    max_write_bytes: int

__all__ = [
    "RelativePath",
    "ExplorerRoot",
    "FileEntry",
    "FileContent",
    "ExcelSheet",
    "ExcelWorkbook",
    "WriteResult",
    "ExtensionPolicy",
    "SizeLimitPolicy",
]
