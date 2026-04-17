"""Domain entities for Post-Edit feature.
Pure dataclasses with no external library dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass
from dataclasses import dataclass, field
from typing import Literal

@dataclass(frozen=True)
class PostEditCellMeta:
    cell: str
    config_path: str
    exists: bool

    def __post_init__(self):  # simple validation
        if not self.cell:
            raise ValueError("cell name cannot be empty")

@dataclass(frozen=True)
class CellMetricMeta:
    cell: str
    a_libs_count: int
    updated_libs_count: int
    complete: bool

    def __post_init__(self):
        if self.a_libs_count < 0 or self.updated_libs_count < 0:
            raise ValueError("library counts cannot be negative")


__all__ = ["PostEditCellMeta", "CellMetricMeta"]