"""QA use cases - application business logic orchestration."""
from typing import List, Optional
from app.domain.qa.entities import QACell, QASummary, QADefaults, QARunRequest, QARunResult, QAJobStatus, CellCheckMatrix
from app.domain.qa.repositories import QARepository, DISPLAY_CHECKS


class ListQACells:
    """Use case: List all QA cells for a project/subproject."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, project: str, subproject: str) -> List[QACell]:
        """List QA cells."""
        return self._repository.list_cells(project, subproject)


class GetQADefaults:
    """Use case: Get default parameters for QA execution."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, project: str, subproject: str, cell: Optional[str] = None, qa_type: str = 'quality') -> QADefaults:
        """Get QA defaults.
        
        Args:
            qa_type: 'quality' or 'process' to determine default run directory
        """
        return self._repository.get_defaults(project, subproject, cell, qa_type)


class ListAvailableCells:
    """Use case: List available cells from data release path."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, data_release_path: str) -> List[str]:
        """List available cells."""
        return self._repository.get_available_cells(data_release_path)


class GetQASummary:
    """Use case: Get QA summary for a cell."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, project: str, subproject: str, cell: str) -> QASummary:
        """Get QA summary."""
        return self._repository.get_summary(project, subproject, cell)


class RunQA:
    """Use case: Execute QA checks."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, project: str, subproject: str, request: QARunRequest) -> QARunResult:
        """Run QA checks."""
        return self._repository.run_qa(project, subproject, request)


class GetQAJobStatus:
    """Use case: Get status of a running QA job."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, job_id: str) -> Optional[QAJobStatus]:
        """Get job status."""
        return self._repository.get_job_status(job_id)


class ListQAChecks:
    """Use case: Get list of available QA checks."""
    
    def execute(self) -> List[str]:
        """Return display checks."""
        return DISPLAY_CHECKS


class GetQAMatrixSummary:
    """Use case: Get QA matrix summary from brief.sum files."""
    
    def __init__(self, repository: QARepository):
        self._repository = repository
    
    def execute(self, project: str, subproject: str, run_dir: str) -> CellCheckMatrix:
        """Get matrix summary with check items as rows and cells as columns."""
        return self._repository.get_matrix_summary(project, subproject, run_dir)
