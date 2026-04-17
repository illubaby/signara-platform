"""Get Defaults Use Case - Retrieve default QC paths for a cell.

This use case:
1. Derives default file paths for QC operations (qcplan, netlist, data, etc.)
2. Optionally parses runall.csh script for existing configuration
3. Returns QCDefaultPaths entity with all configuration
"""

from app.domain.qc.entities import QCDefaultPaths
from app.infrastructure.qc.default_paths_repository import DefaultPathsRepositoryFS


class GetDefaultsUseCase:
    """Use case for retrieving default QC paths for a cell."""

    def __init__(self, defaults_repo: DefaultPathsRepositoryFS):
        """Initialize with defaults repository.
        
        Args:
            defaults_repo: Repository for deriving default paths
        """
        self.defaults_repo = defaults_repo

    def execute(
        self,
        project: str,
        subproject: str,
        cell: str,
        force_defaults: bool = False
    ) -> QCDefaultPaths:
        """Execute use case: get default paths for cell.
        
        Args:
            project: Project name
            subproject: Subproject name
            cell: Cell name
            force_defaults: If True, ignore existing runall.csh and return fresh defaults
            
        Returns:
            QCDefaultPaths entity with all paths and options
        """
        return self.defaults_repo.derive_defaults(
            project,
            subproject,
            cell,
            force_defaults
        )
