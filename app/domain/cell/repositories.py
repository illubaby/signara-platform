from typing import Protocol, List, Optional, Iterable
from app.domain.cell.entities import Cell

class CellRepository(Protocol):
    """Protocol for a repository that manages cells and allows updating editable fields."""

    def list_cells(self, project: str, subproject: str, refresh: bool = False) -> List[Cell]:
        """Lists all cells for a given project and subproject."""
        ...

    def update_cell_pic(self, project: str, subproject: str, cell: str, pic: Optional[str]) -> bool:
        """Update the PIC for a given cell. Returns True if updated successfully."""
        ...

    def batch_update_cell_pic(self, project: str, subproject: str, updates: Iterable[tuple[str, Optional[str]]]) -> int:
        """Batch update PICs for multiple cells. Returns count of updated cells. Uploads to P4 once after all updates."""
        ...

    def batch_update_cell_fields(self, project: str, subproject: str, updates: Iterable[tuple[str, dict]]) -> int:
        """Batch update arbitrary fields for cells. Each update is (cell, {field: value}). Uploads to P4 once. Returns count of cells updated."""
        ...

    def delete_cell(self, project: str, subproject: str, cell: str) -> bool:
        """Delete a cell from the cache. Returns True if deleted successfully. Uploads to P4."""
        ...

    def batch_delete_cells(self, project: str, subproject: str, cells: Iterable[str]) -> int:
        """Delete multiple cells in batch. Returns number of cells deleted and uploads to P4 once."""
        ...

    def add_cell(self, project: str, subproject: str, cell_data: dict) -> bool:
        """Add a new cell to the cache. Returns True if added successfully. Uploads to P4."""
        ...
