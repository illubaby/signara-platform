"""Task Queue Repository - Filesystem implementation for QC task queue management.

DEPRECATED: Use app.infrastructure.fs.task_queue_repository_fs instead.
This file kept temporarily for backwards compatibility during migration.
"""

from pathlib import Path
from app.interface.http.schemas.task_queue import (
    TaskQueueRequestSchema as TaskQueueRequest,
    TaskQueueResultSchema as TaskQueueResult,
    TaskQueueStatusSchema as TaskQueueStatus
)
from app.domain.task_queue.entities import TaskQueueConfig
from app.infrastructure.fs.task_queue_repository_fs import TaskQueueRepositoryFS as NewRepo


class TaskQueueRepositoryFS:
    """Filesystem-based task queue repository (DEPRECATED - delegates to new implementation)."""
    
    def __init__(self):
        self._repo = NewRepo()
    
    def write_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str,
        req: TaskQueueRequest
    ) -> TaskQueueResult:
        """Delegate to new repository implementation."""
        config = TaskQueueConfig(
            normal_queue_no_prefix=req.normal_queue_no_prefix,
            job_scheduler=req.job_scheduler,
            run_list_maxsize=req.run_list_maxsize,
            normal_queue=req.normal_queue,
            statistical_montecarlo_sample_size=req.statistical_montecarlo_sample_size,
            netlist_max_sweeps=req.netlist_max_sweeps,
            simulator=req.simulator,
            write_monte_carlo=req.write_monte_carlo
        )
        result = self._repo.write_task_queue(cell_dir, project, subproject, cell, config)
        return TaskQueueResult(
            project=result.project,
            subproject=result.subproject,
            cell=result.cell,
            sis_task_queue_path=result.sis_task_queue_path,
            bytes_written_task_queue=result.bytes_written_task_queue,
            monte_carlo_settings_path=result.monte_carlo_settings_path,
            bytes_written_montecarlo=result.bytes_written_montecarlo,
            simulator=result.simulator,
            note=result.note
        )
    
    def read_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str
    ) -> TaskQueueStatus:
        """Delegate to new repository implementation."""
        status = self._repo.read_task_queue(cell_dir, project, subproject, cell)
        values_schema = TaskQueueRequest(
            normal_queue_no_prefix=status.config.normal_queue_no_prefix,
            job_scheduler=status.config.job_scheduler,
            run_list_maxsize=status.config.run_list_maxsize,
            normal_queue=status.config.normal_queue,
            statistical_montecarlo_sample_size=status.config.statistical_montecarlo_sample_size,
            netlist_max_sweeps=status.config.netlist_max_sweeps,
            simulator=status.config.simulator,
            write_monte_carlo=status.config.write_monte_carlo
        )
        return TaskQueueStatus(
            project=status.project,
            subproject=status.subproject,
            cell=status.cell,
            exists_task_queue=status.exists_task_queue,
            exists_monte_carlo=status.exists_monte_carlo,
            values=values_schema,
            simulator=status.simulator,
            sis_task_queue_path=status.sis_task_queue_path,
            monte_carlo_settings_path=status.monte_carlo_settings_path,
            note=status.note
        )
