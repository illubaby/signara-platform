"""FastAPI dependency providers for Explorer use cases.

Central place for wiring settings/infrastructure into application layer.
"""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path

from app.infrastructure.settings.settings import get_settings
from app.domain.explorer.models import ExplorerRoot, ExtensionPolicy, SizeLimitPolicy
from app.infrastructure.explorer.fs_repository import FileSystemExplorerRepository
from app.infrastructure.explorer.excel_reader import PandasExcelReader
from app.application.explorer.use_cases import (
    ListDirectory, ReadFile, WriteFile
)

@lru_cache
def _extension_policy() -> ExtensionPolicy:
    s = get_settings()
    return ExtensionPolicy(allowed=list(s.writable_ext_allow), blocked=list(s.writable_ext_block))

@lru_cache
def _size_policy() -> SizeLimitPolicy:
    s = get_settings()
    return SizeLimitPolicy(max_read_bytes=512*1024, max_write_bytes=s.explorer_max_write_bytes)

@lru_cache
def _root(path: str) -> ExplorerRoot:
    return ExplorerRoot(Path(path))

# These factories assume caller passes an absolute root (project timing path or global root)

def get_list_directory_use_case(root_path: str) -> ListDirectory:
    repo = FileSystemExplorerRepository(Path(root_path), excel_reader=PandasExcelReader())
    return ListDirectory(_root(root_path), repo)

def get_read_file_use_case(root_path: str) -> ReadFile:
    repo = FileSystemExplorerRepository(Path(root_path), excel_reader=PandasExcelReader())
    return ReadFile(_root(root_path), repo)

def get_write_file_use_case(root_path: str) -> WriteFile:
    repo = FileSystemExplorerRepository(Path(root_path), excel_reader=PandasExcelReader())
    return WriteFile(_root(root_path), repo, _extension_policy(), _size_policy())

__all__ = [
    "get_list_directory_use_case",
    "get_read_file_use_case",
    "get_write_file_use_case",
]
