"""Common helpers for resolving project/subproject timing roots.

Infrastructure layer - filesystem path construction.
"""
from __future__ import annotations
from pathlib import Path
from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.domain.common.validation import validate_component

class TimingPaths:
    """Constructs filesystem paths for timing project structure.
    
    Centralizes path construction to reduce duplication across the application.
    """
    
    def __init__(self, project: str, subproject: str):
        validate_component(project, 'project')
        validate_component(subproject, 'subproject')
        self.project = project
        self.subproject = subproject
        self.base = Path(PROJECTS_BASE) / project / subproject
        self.timing_root = self.base / 'design' / 'timing'
        self.release_process_dir = self.timing_root / 'release' / 'process'
        self.qa_quality_root = self.timing_root / 'quality' / '4_qc'

    def ensure_release_process_dir(self) -> None:
        """Create release process directory if it doesn't exist."""
        self.release_process_dir.mkdir(parents=True, exist_ok=True)

    def qa_run_dir(self, qa_type: str = 'quality') -> Path:
        """Return QA run directory based on type.
        
        Args:
            qa_type: 'quality' (default: quality/3_qa) or 'process' (release/process)
        """
        if qa_type == 'process':
            return self.timing_root / 'release' / 'process'
        else:
            return self.timing_root / 'quality' / '3_qa'

    def qa_cell_dir(self, cell: str) -> Path:
        """Return QA cell directory path."""
        validate_component(cell, 'cell')
        return self.qa_quality_root / cell
    
    # QC-specific paths
    @property
    def qc_root(self) -> Path:
        """Return quality/4_qc root directory."""
        return self.qa_quality_root
    
    def qc_cell_root(self, cell: str) -> Path:
        """Return QC cell directory path."""
        validate_component(cell, 'cell')
        return self.qc_root / cell
    
    def qc_testbench_root(self, cell: str, testbench: str) -> Path:
        """Return testbench directory (canonical or legacy).
        
        Tries canonical path first: simulations_{cell}/{testbench}
        Falls back to legacy: simulation_{cell}/{testbench}
        """
        validate_component(cell, 'cell')
        validate_component(testbench, 'testbench')
        
        canonical = self.qc_cell_root(cell) / f"simulations_{cell}" / testbench
        legacy = self.qc_root / f"simulation_{cell}" / testbench
        return canonical if canonical.exists() else legacy

__all__ = ["TimingPaths"]
