"""Port interfaces (Protocols) for QC feature.

Application layer will depend on these, infrastructure will implement them.
"""
from __future__ import annotations
from typing import Protocol, List, Set, Optional, Dict, Any
from .entities import QCCellMeta, PVTRowMeta, QCDefaultPaths, TableRowData

class QCCellRepository(Protocol):
    def list_local_cells(self, project: str, subproject: str) -> List[QCCellMeta]: ...
    def list_all_cells(self, project: str, subproject: str) -> List[QCCellMeta]: ...  # may merge P4V cells

class QCP4VRepository(Protocol):
    def list_cells(self, project: str) -> Set[str]: ...
    def get_last_change(self, depot_glob: str) -> Optional[str]: ...

class QCTestbenchRepository(Protocol):
    def list_testbenches(self, project: str, subproject: str, cell: str) -> List[str]: ...
    def list_pvts(self, testbench_dir: str) -> List[PVTRowMeta]: ...

class QCDefaultsRepository(Protocol):
    def parse_runall(self, runall_path: str) -> Dict[str, Any]: ...
    def derive_defaults(self, project: str, subproject: str, cell: str, force_defaults: bool = False) -> QCDefaultPaths: ...

class QCScriptBuilder(Protocol):
    def build_runall(self, cell: str, params: Dict[str, Any], project: str, subproject: str) -> str: ...

class QCTablesRepository(Protocol):
    def build_tables(self, timing_paths: Optional[str], data: Optional[str]) -> Dict[str, List[TableRowData]]: ...

__all__ = [
    "QCCellRepository",
    "QCP4VRepository",
    "QCTestbenchRepository",
    "QCDefaultsRepository",
    "QCScriptBuilder",
    "QCTablesRepository",
]