"""Use cases for PVT management (Phase 5 - Clean Architecture migration).

This module handles business logic for:
- Listing available PVTs from configure_pvt.tcl (Perforce)
- Listing NT cell PVTs from pvt_corners.lst (filesystem)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Protocol


# Port definitions
class PerforceRepository(Protocol):
    """Repository protocol for reading PVT configurations from Perforce."""
    
    def read_configure_pvt(self, project: str, subproject: str, internal: bool = False) -> List[str]:
        """Read and parse configure_pvt.tcl to extract PVT corners.
        
        Returns:
            List of PVT corner names (e.g., ['FF_0p72_125C', 'SS_0p675_m40C'])
        """
        ...


class CellRepository(Protocol):
    """Repository protocol for reading NT cell data from filesystem."""
    
    def collect_nt_pvts(self, project: str, subproject: str, cell: str) -> List[str]:
        """Read pvt_corners.lst for an NT cell.
        
        Returns:
            List of PVT corner names from the NT cell's pvt_corners.lst file
        """
        ...


# Input/Output DTOs
@dataclass(frozen=True)
class GetPvtListInput:
    project: str
    subproject: str
    internal: bool = False


@dataclass(frozen=True)
class GetPvtListOutput:
    pvts: List[str]
    note: str


@dataclass(frozen=True)
class GetNtPvtListInput:
    project: str
    subproject: str
    cell: str


@dataclass(frozen=True)
class GetNtPvtListOutput:
    pvts: List[str]
    note: str


# Use Cases
class GetPvtList:
    """Retrieve list of available PVTs for SiS characterization."""
    
    def __init__(self, perforce_repo: PerforceRepository):
        self._repo = perforce_repo
    
    def execute(self, input_dto: GetPvtListInput) -> GetPvtListOutput:
        """Execute the use case.
        
        Args:
            input_dto: Project and subproject identifiers
            
        Returns:
            GetPvtListOutput with PVT list and note
            
        Raises:
            ValueError: If no PVTs found or file missing
        """
        pvts = self._repo.read_configure_pvt(input_dto.project, input_dto.subproject, input_dto.internal)
        
        if not pvts:
            raise ValueError("No PVTs found in configure_pvt.tcl")
        
        suffix = " (internal)" if input_dto.internal else ""
        note = f"Found {len(pvts)} PVTs in configure_pvt.tcl{suffix}"
        return GetPvtListOutput(pvts=pvts, note=note)


class GetNtPvtList:
    """Retrieve list of available PVTs for NT cell characterization."""
    
    def __init__(self, cell_repo: CellRepository):
        self._repo = cell_repo
    
    def execute(self, input_dto: GetNtPvtListInput) -> GetNtPvtListOutput:
        """Execute the use case.
        
        Args:
            input_dto: Project, subproject, and cell identifiers
            
        Returns:
            GetNtPvtListOutput with PVT list and note (empty list if pvt_corners.lst not found)
        """
        pvts = self._repo.collect_nt_pvts(
            input_dto.project,
            input_dto.subproject,
            input_dto.cell
        )
        
        if not pvts:
            note = f"No PVTs found for NT cell {input_dto.cell}. Run Setup to generate pvt_corners.lst"
            return GetNtPvtListOutput(pvts=[], note=note)
        
        note = f"Found {len(pvts)} PVTs in pvt_corners.lst for NT cell {input_dto.cell}"
        return GetNtPvtListOutput(pvts=pvts, note=note)


__all__ = [
    "PerforceRepository",
    "CellRepository",
    "GetPvtList", "GetPvtListInput", "GetPvtListOutput",
    "GetNtPvtList", "GetNtPvtListInput", "GetNtPvtListOutput",
]
