"""Domain entities for SAF (SiS/NT) timing module (Phase 1 extraction).

Kept intentionally close to legacy structure for incremental migration:
`Cell` mirrors legacy `CellMeta` fields so routers/services remain compatible.

Later phases may rename `cell` -> `name` and introduce semantic types.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Cell:
    cell: str              # legacy field name
    type: str              # 'sis' or 'nt' (will become Enum later)
    pvts: List[str]
    pvt_count: int         # duplicated count; retained for compatibility
    netlist_version: str
    final_libs: int

    def __post_init__(self) -> None:
        # Ensure pvt_count remains consistent; adjust silently (Phase 1 leniency).
        actual = len(self.pvts)
        if self.pvt_count != actual:
            self.pvt_count = actual

__all__ = ["Cell"]


@dataclass
class SafSyncStatus:
    synced: bool
    note: str
    error: Optional[str] = None

__all__.append("SafSyncStatus")
