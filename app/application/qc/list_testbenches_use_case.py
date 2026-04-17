"""List Testbenches Use Case - Retrieve testbenches for a QC cell.

This use case scans the filesystem for testbench directories under:
- simulations_{cell}/ (canonical)
- simulation_{cell}/ (legacy)
"""

from typing import List
from app.infrastructure.qc.testbench_repository_fs import TestbenchRepositoryFS


class ListTestbenchesUseCase:
    """Use case for listing testbenches for a QC cell."""

    def __init__(self, tb_repo: TestbenchRepositoryFS):
        """Initialize with testbench repository.
        
        Args:
            tb_repo: Repository for testbench filesystem operations
        """
        self.tb_repo = tb_repo

    def execute(self, project: str, subproject: str, cell: str) -> List[str]:
        """Execute use case: list all testbenches for cell.
        
        Args:
            project: Project name
            subproject: Subproject name
            cell: Cell name
            
        Returns:
            List of testbench directory names (sorted)
        """
        return self.tb_repo.list_testbenches(project, subproject, cell)
