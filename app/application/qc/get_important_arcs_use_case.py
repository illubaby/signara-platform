"""Get Important Arcs Use Case - Retrieve important testbench numbers.

This use case reads the important_arc.csv file from the cell directory
and extracts testbench numbers marked as important for highlighting in UI.
"""

from typing import List
from pathlib import Path
import csv
from app.infrastructure.fs.timing_paths import TimingPaths


class GetImportantArcsUseCase:
    """Use case for retrieving important arc numbers from CSV."""

    def execute(self, project: str, subproject: str, cell: str) -> List[int]:
        """Execute use case: get important testbench numbers.
        
        Args:
            project: Project name
            subproject: Subproject name
            cell: Cell name
            
        Returns:
            Sorted list of important testbench numbers (empty if file not found)
        """
        tp = TimingPaths(project, subproject)
        cell_root = tp.qc_cell_root(cell)
        important_arc_file = cell_root / "important_arc.csv"
        
        if not important_arc_file.exists():
            return []
        
        important_numbers: List[int] = []
        
        try:
            with important_arc_file.open('r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row:
                        continue
                    # Try to extract numbers from each cell in the row
                    for cell_value in row:
                        cell_value = cell_value.strip()
                        # Skip headers or non-numeric values
                        if cell_value.lower() in ('testbench', 'number', 'id', 'tb', ''):
                            continue
                        # Try to parse as integer
                        try:
                            num = int(cell_value)
                            if num not in important_numbers:
                                important_numbers.append(num)
                        except ValueError:
                            # Not a number, skip
                            continue
        except Exception:
            # File read error - return empty list
            return []
        
        # Sort for consistency
        important_numbers.sort()
        return important_numbers
