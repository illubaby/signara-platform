"""Application layer ports (interfaces) for Explorer.

Define boundary abstractions implemented by infrastructure and consumed
by use cases.
"""
from __future__ import annotations
from typing import List
from pathlib import Path

from app.domain.explorer.models import (
    RelativePath, FileEntry, FileContent, WriteResult, ExcelWorkbook
)

class ExplorerRepository:
    """Filesystem-like abstraction for listing, reading & writing.

    Implementations should honor `allow_external` when resolving symlinks
    that target outside the declared root (read and list operations only).
    Writes must always remain confined to root regardless of the flag.
    """

    def list(self, relative: RelativePath | None, *, allow_external: bool) -> List[FileEntry]:  # pragma: no cover - interface
        raise NotImplementedError

    def read(self, relative: RelativePath, *, allow_external: bool) -> FileContent:  # pragma: no cover - interface
        raise NotImplementedError

    def write(self, relative: RelativePath, content: str) -> WriteResult:  # pragma: no cover - interface
        raise NotImplementedError

class ExcelReaderPort:
    """Abstraction for reading Excel files into an ExcelWorkbook."""
    def read_workbook(self, path: Path, max_rows: int) -> ExcelWorkbook:  # pragma: no cover - interface
        raise NotImplementedError

__all__ = ["ExplorerRepository", "ExcelReaderPort"]
