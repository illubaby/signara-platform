"""File operations use cases for SAF PVT directories (Phase 5 migration).

Provides application-layer logic for file browsing, reading, and writing
within SAF cell PVT directories.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

from app.domain.saf.repositories import SafCellRepository
from app.application.explorer.use_cases import (
    ListDirectory, ListDirectoryInput,
    ReadFile, ReadFileInput,
    WriteFile, WriteFileInput,
)


@dataclass
class ListPvtFilesInput:
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str = ""


@dataclass
class ListPvtFilesOutput:
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str
    entries: List[Dict[str, Any]]


@dataclass
class ReadPvtFileInput:
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str


@dataclass
class ReadPvtFileOutput:
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str
    name: str
    size: int
    is_text: bool
    truncated: bool
    content: str | None


@dataclass
class WritePvtFileInput:
    project: str
    subproject: str
    cell: str
    pvt: str
    path: str
    content: str


@dataclass
class WritePvtFileOutput:
    project: str
    subproject: str
    cell: str
    pvt: str
    name: str
    bytes: int
    created: bool
    note: str


class ListPvtFiles:
    """List files in a SAF cell PVT directory."""
    
    def __init__(self, cell_repo: SafCellRepository) -> None:
        self.cell_repo = cell_repo
    
    def execute(self, inp: ListPvtFilesInput) -> ListPvtFilesOutput:
        # Resolve PVT root directory
        pvt_root = self._resolve_pvt_root(inp.project, inp.subproject, inp.cell, inp.pvt)
        
        # Use explorer use case for listing
        from app.interface.dependencies.explorer_dep import get_list_directory_use_case
        uc = get_list_directory_use_case(str(pvt_root))
        out = uc.execute(ListDirectoryInput(relative=inp.path or '', allow_external=True))
        
        entries = [e.__dict__ for e in out.entries]
        
        return ListPvtFilesOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            pvt=inp.pvt,
            path=inp.path,
            entries=entries
        )
    
    def _resolve_pvt_root(self, project: str, subproject: str, cell: str, pvt: str) -> Path:
        """Return root directory for a given cell & PVT (char_ prefix)."""
        sis_root = self.cell_repo.resolve_sis_root(project, subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {cell}")
        
        # Accept either raw pvt (e.g. FF_0p72_125C) or with char_ prefix from UI
        if pvt.startswith('char_'):
            pvt_dir = cell_dir / pvt
        else:
            pvt_dir = cell_dir / f"char_{pvt}"
        
        if not pvt_dir.exists() or not pvt_dir.is_dir():
            raise ValueError(f"PVT directory not found: {pvt}")
        
        return pvt_dir


class ReadPvtFile:
    """Read a file from a SAF cell PVT directory."""
    
    def __init__(self, cell_repo: SafCellRepository) -> None:
        self.cell_repo = cell_repo
    
    def execute(self, inp: ReadPvtFileInput) -> ReadPvtFileOutput:
        # Resolve PVT root directory
        pvt_root = self._resolve_pvt_root(inp.project, inp.subproject, inp.cell, inp.pvt)
        
        # Use explorer use case for reading
        from app.interface.dependencies.explorer_dep import get_read_file_use_case
        uc = get_read_file_use_case(str(pvt_root))
        out = uc.execute(ReadFileInput(relative=inp.path, allow_external=True))
        
        fc = out.content
        
        return ReadPvtFileOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            pvt=inp.pvt,
            path=inp.path,
            name=fc.name,
            size=fc.size,
            is_text=fc.is_text,
            truncated=fc.truncated,
            content=fc.content if fc.is_text else None
        )
    
    def _resolve_pvt_root(self, project: str, subproject: str, cell: str, pvt: str) -> Path:
        """Return root directory for a given cell & PVT (char_ prefix)."""
        sis_root = self.cell_repo.resolve_sis_root(project, subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {cell}")
        
        # Accept either raw pvt (e.g. FF_0p72_125C) or with char_ prefix from UI
        if pvt.startswith('char_'):
            pvt_dir = cell_dir / pvt
        else:
            pvt_dir = cell_dir / f"char_{pvt}"
        
        if not pvt_dir.exists() or not pvt_dir.is_dir():
            raise ValueError(f"PVT directory not found: {pvt}")
        
        return pvt_dir


class WritePvtFile:
    """Write a file to a SAF cell PVT directory."""
    
    def __init__(self, cell_repo: SafCellRepository) -> None:
        self.cell_repo = cell_repo
    
    def execute(self, inp: WritePvtFileInput) -> WritePvtFileOutput:
        # Resolve PVT root directory
        pvt_root = self._resolve_pvt_root(inp.project, inp.subproject, inp.cell, inp.pvt)
        
        # Use explorer use case for writing
        from app.interface.dependencies.explorer_dep import get_write_file_use_case
        uc = get_write_file_use_case(str(pvt_root))
        out = uc.execute(WriteFileInput(relative=inp.path, content=inp.content))
        
        result = out.result
        
        return WritePvtFileOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            pvt=inp.pvt,
            name=result.name,
            bytes=result.bytes_written,
            created=result.created,
            note="Saved"
        )
    
    def _resolve_pvt_root(self, project: str, subproject: str, cell: str, pvt: str) -> Path:
        """Return root directory for a given cell & PVT (char_ prefix)."""
        sis_root = self.cell_repo.resolve_sis_root(project, subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {cell}")
        
        # Accept either raw pvt (e.g. FF_0p72_125C) or with char_ prefix from UI
        if pvt.startswith('char_'):
            pvt_dir = cell_dir / pvt
        else:
            pvt_dir = cell_dir / f"char_{pvt}"
        
        if not pvt_dir.exists() or not pvt_dir.is_dir():
            raise ValueError(f"PVT directory not found: {pvt}")
        
        return pvt_dir


__all__ = [
    "ListPvtFiles", "ListPvtFilesInput", "ListPvtFilesOutput",
    "ReadPvtFile", "ReadPvtFileInput", "ReadPvtFileOutput",
    "WritePvtFile", "WritePvtFileInput", "WritePvtFileOutput",
]
