"""Task Queue use cases.

Application layer logic for task queue management.
"""
from dataclasses import dataclass
from pathlib import Path
from app.domain.task_queue.entities import TaskQueueConfig, TaskQueueResult, TaskQueueStatus
from app.domain.task_queue.repositories import TaskQueueRepository
from app.domain.saf.repositories import SafCellRepository


@dataclass
class WriteTaskQueueInput:
    """Input for writing task queue configuration."""
    project: str
    subproject: str
    cell: str
    config: TaskQueueConfig


@dataclass
class GetTaskQueueStatusInput:
    """Input for getting task queue status."""
    project: str
    subproject: str
    cell: str


class WriteTaskQueue:
    """Write task queue configuration files for a cell."""
    
    def __init__(
        self,
        task_queue_repo: TaskQueueRepository,
        cell_repo: SafCellRepository
    ) -> None:
        self.task_queue_repo = task_queue_repo
        self.cell_repo = cell_repo
    
    def execute(self, inp: WriteTaskQueueInput) -> TaskQueueResult:
        """Execute the write task queue use case."""
        # Resolve SiS root directory
        sis_root = self.cell_repo.resolve_sis_root(inp.project, inp.subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / inp.cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {inp.cell}")
        
        return self.task_queue_repo.write_task_queue(
            cell_dir=cell_dir,
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            config=inp.config
        )


class GetTaskQueueStatus:
    """Get task queue status for a cell."""
    
    def __init__(
        self,
        task_queue_repo: TaskQueueRepository,
        cell_repo: SafCellRepository
    ) -> None:
        self.task_queue_repo = task_queue_repo
        self.cell_repo = cell_repo
    
    def execute(self, inp: GetTaskQueueStatusInput) -> TaskQueueStatus:
        """Execute the get task queue status use case."""
        # Resolve SiS root directory
        sis_root = self.cell_repo.resolve_sis_root(inp.project, inp.subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / inp.cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {inp.cell}")
        
        return self.task_queue_repo.read_task_queue(
            cell_dir=cell_dir,
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell
        )
