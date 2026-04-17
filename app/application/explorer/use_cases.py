"""Explorer application layer use cases.

Each use case encapsulates orchestration & policy enforcement but no
knowledge of HTTP or persistence details.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from app.domain.explorer.models import (
    RelativePath, ExplorerRoot, FileEntry, FileContent, WriteResult,
    ExtensionPolicy, SizeLimitPolicy
)
from app.domain.explorer.errors import FileNotFoundDomain, PolicyViolation
from .ports import ExplorerRepository

# -------------------- DTOs --------------------
@dataclass(frozen=True)
class ListDirectoryInput:
    relative: Optional[str]
    allow_external: bool = False

@dataclass(frozen=True)
class ListDirectoryOutput:
    entries: list[FileEntry]

@dataclass(frozen=True)
class ReadFileInput:
    relative: str
    allow_external: bool = False

@dataclass(frozen=True)
class ReadFileOutput:
    content: FileContent

@dataclass(frozen=True)
class WriteFileInput:
    relative: str
    content: str

@dataclass(frozen=True)
class WriteFileOutput:
    result: WriteResult

# -------------------- Use Cases --------------------
class ListDirectory:
    def __init__(self, root: ExplorerRoot, repo: ExplorerRepository):
        self.root = root
        self.repo = repo

    def execute(self, inp: ListDirectoryInput) -> ListDirectoryOutput:
        rel = RelativePath(inp.relative or "") if inp.relative else RelativePath("")
        entries = self.repo.list(rel if not rel.is_root() else None, allow_external=inp.allow_external)
        return ListDirectoryOutput(entries=entries)

class ReadFile:
    def __init__(self, root: ExplorerRoot, repo: ExplorerRepository):
        self.root = root
        self.repo = repo

    def execute(self, inp: ReadFileInput) -> ReadFileOutput:
        rel = RelativePath(inp.relative)
        content = self.repo.read(rel, allow_external=inp.allow_external)
        if content.content is None and not content.excel:
            # Domain-level not found distinction if repo uses sentinel
            pass
        return ReadFileOutput(content=content)

class WriteFile:
    def __init__(self, root: ExplorerRoot, repo: ExplorerRepository, ext_policy: ExtensionPolicy, size_policy: SizeLimitPolicy):
        self.root = root
        self.repo = repo
        self.ext_policy = ext_policy
        self.size_policy = size_policy

    def execute(self, inp: WriteFileInput) -> WriteFileOutput:
        rel = RelativePath(inp.relative)
        # Policy checks before repository call
        ext = "." + inp.relative.split('.')[-1] if '.' in inp.relative else ''
        if not self.ext_policy.is_allowed(ext):
            raise PolicyViolation(f"Extension '{ext}' not allowed")
        if len(inp.content.encode('utf-8')) > self.size_policy.max_write_bytes:
            raise PolicyViolation("Content exceeds max write size")
        result = self.repo.write(rel, inp.content)
        return WriteFileOutput(result=result)

__all__ = [
    "ListDirectory", "ReadFile", "WriteFile",
    "ListDirectoryInput", "ListDirectoryOutput",
    "ReadFileInput", "ReadFileOutput",
    "WriteFileInput", "WriteFileOutput",
]
