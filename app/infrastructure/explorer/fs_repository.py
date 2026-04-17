"""Filesystem-backed ExplorerRepository implementation.

Adapts the existing logic from utils.file_explorer into the ExplorerRepository
port expected by application layer use cases.
"""
from __future__ import annotations
from pathlib import Path
from typing import List

from app.application.explorer.ports import ExplorerRepository
from app.domain.explorer.models import (
    RelativePath, FileEntry, FileContent, WriteResult, ExcelWorkbook, ExcelSheet
)
from app.domain.explorer.errors import PathViolation, FileNotFoundDomain
from app.infrastructure.settings.settings import get_settings
from app.infrastructure.logging.logging_config import get_logger

import mimetypes

class FileSystemExplorerRepository(ExplorerRepository):
    def __init__(self, root: Path, excel_reader=None):
        self.root = root
        self._settings = get_settings()
        self._log = get_logger("explorer.fs")
        self._max_read = 512 * 1024  # keep same default for now
        self._excel_reader = excel_reader  # optional Excel adapter

    # --- Internal helpers ---
    def _resolve(self, rel: RelativePath | None, *, allow_external: bool) -> Path:
        """Resolve a relative path against the repository root.

        Previous implementation always rejected symlinks pointing outside the
        root. This prevented navigating into legitimate external directories
        when the UI requested it ("allow_external=True"). We now allow traversal
        through a symlink that resides *inside* the root when external access
        is explicitly permitted.

        Security: ``RelativePath`` already forbids ``..`` and absolute paths,
        so a user can only reference names that exist underneath ``root``. We
        only waive the root containment check when ``allow_external`` is True.
        """
        if rel is None or rel.is_root():
            return self.root
        candidate_unresolved = self.root / rel.value
        # Fast path: disallow external unless explicitly allowed
        if not allow_external:
            candidate = candidate_unresolved.resolve()
            root_resolved = self.root.resolve()
            if not str(candidate).startswith(str(root_resolved)):
                raise PathViolation("Path escapes root")
            return candidate
        # External allowed: resolve but skip containment enforcement. If the
        # first component does not exist we still just return its resolved
        # value (normal Path behavior for non-existent). If it exists and is a
        # symlink we follow it; otherwise we behave like internal navigation.
        try:
            return candidate_unresolved.resolve()
        except Exception:
            # On resolution failure (rare), fall back to unresolved path.
            return candidate_unresolved

    def list(self, relative: RelativePath | None, *, allow_external: bool) -> List[FileEntry]:
        base = self._resolve(relative, allow_external=allow_external)
        if not base.exists() or not base.is_dir():
            return []
        out: List[FileEntry] = []
        for entry in sorted(base.iterdir(), key=lambda p: p.name.lower()):
            try:
                is_dir = entry.is_dir()
                external = False
                if allow_external:
                    try:
                        resolved = entry.resolve()
                        external = not str(resolved).startswith(str(self.root.resolve()))
                    except Exception:
                        external = False
                size = None
                if not is_dir:
                    try:
                        size = entry.stat().st_size
                    except Exception:
                        size = None
                out.append(FileEntry(
                    name=entry.name,
                    is_dir=is_dir,
                    is_symlink=entry.is_symlink(),
                    external=external,
                    size=size
                ))
            except Exception:
                continue
        return out

    def read(self, relative: RelativePath, *, allow_external: bool) -> FileContent:
        path = self._resolve(relative, allow_external=allow_external)
        if not path.exists() or not path.is_file():
            raise FileNotFoundDomain(relative.value)
        size = path.stat().st_size
        ext = path.suffix.lower()

        # Excel handling via adapter
        if ext in {'.xlsx', '.xls', '.xlsm'} and self._excel_reader:
            try:
                wb = self._excel_reader.read_workbook(path, max_rows=1000)
                return FileContent(
                    relative=relative,
                    name=path.name,
                    size=size,
                    is_text=False,
                    truncated=wb.truncated,
                    content=None,
                    excel=wb
                )
            except Exception as e:
                # Fallback to non-text read with error message embedded
                sheet = ExcelSheet(
                    name="error",
                    columns=["message"],
                    rows=[[str(e)]],
                    row_count=1,
                    truncated=False,
                    error=str(e)
                )
                wb = ExcelWorkbook(sheets={"error": sheet}, sheet_names=["error"], truncated=False)
                return FileContent(
                    relative=relative,
                    name=path.name,
                    size=size,
                    is_text=False,
                    truncated=False,
                    content=None,
                    excel=wb
                )

        is_text = self._is_text(path, size)
        truncated = False
        content_str = None
        if is_text:
            data = path.read_bytes()
            if len(data) > self._max_read:
                data = data[: self._max_read]
                truncated = True
            try:
                content_str = data.decode('utf-8', errors='replace')
            except Exception:
                content_str = data.decode('latin-1', errors='replace')
        return FileContent(
            relative=relative,
            name=path.name,
            size=size,
            is_text=is_text,
            truncated=truncated,
            content=content_str,
            excel=None
        )

    def write(self, relative: RelativePath, content: str) -> WriteResult:
        # Writes never permit external traversal; enforce sandbox.
        path = self._resolve(relative, allow_external=False)
        parent = path.parent
        if not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
        if not parent.is_dir():
            raise PathViolation("Parent path is not a directory")
        exists = path.exists()
        data = content.encode('utf-8')
        path.write_bytes(data)
        if self._settings.audit_explorer_writes:
            self._log.info("explorer_write path=%s size=%d created=%s", path, len(data), (not exists))
        return WriteResult(name=path.name, bytes_written=len(data), created=not exists)

    # --- Heuristics ---
    def _is_text(self, path: Path, size: int) -> bool:
        if size == 0:
            return True
        try:
            sample = path.read_bytes()[:2048]
            if b'\x00' in sample:
                return False
        except Exception:
            return False
        mime, _ = mimetypes.guess_type(path.name)
        if mime and mime.startswith('text/'):
            return True
        return True

__all__ = ["FileSystemExplorerRepository"]
