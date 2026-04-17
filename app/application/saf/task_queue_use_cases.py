"""Task Queue use cases for SAF (Phase 5 migration).

DEPRECATED: Use app.application.task_queue.use_cases instead.
This file kept temporarily for backwards compatibility during migration.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.domain.saf.repositories import SafCellRepository
from app.domain.task_queue.entities import TaskQueueConfig
from app.infrastructure.fs.task_queue_repository_fs import TaskQueueRepositoryFS


@dataclass
class GetTaskQueueStatusInput:
    project: str
    subproject: str
    cell: str


@dataclass
class GetTaskQueueStatusOutput:
    project: str
    subproject: str
    cell: str
    exists_task_queue: bool
    exists_monte_carlo: bool
    values: dict
    simulator: str
    sis_task_queue_path: str | None
    monte_carlo_settings_path: str | None
    note: str | None


class GetTaskQueueStatus:
    """Get task queue status for a SAF cell (DEPRECATED - delegates to new implementation)."""
    
    def __init__(self, cell_repo: SafCellRepository) -> None:
        self.cell_repo = cell_repo
        self.repo = TaskQueueRepositoryFS()
    
    def execute(self, inp: GetTaskQueueStatusInput) -> GetTaskQueueStatusOutput:
        # Resolve SiS root directory
        sis_root = self.cell_repo.resolve_sis_root(inp.project, inp.subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / inp.cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {inp.cell}")
        
        # Use new repository to read status
        status = self.repo.read_task_queue(cell_dir, inp.project, inp.subproject, inp.cell)
        
        return GetTaskQueueStatusOutput(
            project=status.project,
            subproject=status.subproject,
            cell=status.cell,
            exists_task_queue=status.exists_task_queue,
            exists_monte_carlo=status.exists_monte_carlo,
            values={
                'normal_queue_no_prefix': status.config.normal_queue_no_prefix,
                'job_scheduler': status.config.job_scheduler,
                'run_list_maxsize': status.config.run_list_maxsize,
                'normal_queue': status.config.normal_queue,
                'statistical_montecarlo_sample_size': status.config.statistical_montecarlo_sample_size,
                'netlist_max_sweeps': status.config.netlist_max_sweeps,
                'simulator': status.config.simulator,
                'statistical_simulation_points': status.config.statistical_simulation_points,
                'write_monte_carlo': status.config.write_monte_carlo,
            },
            simulator=status.simulator,
            sis_task_queue_path=status.sis_task_queue_path,
            monte_carlo_settings_path=status.monte_carlo_settings_path,
            note=status.note,
        )


@dataclass
class WriteTaskQueueInput:
    project: str
    subproject: str
    cell: str
    request: dict  # Changed from TaskQueueRequest to dict for compatibility


@dataclass
class WriteTaskQueueOutput:
    project: str
    subproject: str
    cell: str
    sis_task_queue_path: str
    bytes_written_task_queue: int
    monte_carlo_settings_path: str | None
    bytes_written_montecarlo: int | None
    simulator: str
    note: str | None


class WriteTaskQueue:
    """Write task queue configuration files for a SAF cell (DEPRECATED - delegates to new implementation)."""
    
    def __init__(self, cell_repo: SafCellRepository) -> None:
        self.cell_repo = cell_repo
        self.repo = TaskQueueRepositoryFS()
    
    def execute(self, inp: WriteTaskQueueInput) -> WriteTaskQueueOutput:
        # Resolve SiS root directory
        sis_root = self.cell_repo.resolve_sis_root(inp.project, inp.subproject)
        if not sis_root:
            raise ValueError("SiS directory not found")
        
        cell_dir = Path(sis_root) / inp.cell
        if not cell_dir.exists():
            raise ValueError(f"Cell directory not found: {inp.cell}")
        
        # Convert dict to TaskQueueConfig
        config = TaskQueueConfig(
            normal_queue_no_prefix=inp.request.get('normal_queue_no_prefix', '1'),
            job_scheduler=inp.request.get('job_scheduler', 'lsf'),
            run_list_maxsize=inp.request.get('run_list_maxsize', '100'),
            normal_queue=inp.request.get('normal_queue', '-app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'),
            statistical_montecarlo_sample_size=inp.request.get('statistical_montecarlo_sample_size', '250'),
            netlist_max_sweeps=inp.request.get('netlist_max_sweeps', '1000'),
            simulator=inp.request.get('simulator', 'primesim'),
            statistical_simulation_points=inp.request.get('statistical_simulation_points', '{1 3 5 7 9 11 13 15 17 19 21 23 25}'),
            write_monte_carlo=inp.request.get('write_monte_carlo', True),
        )
        
        # Use new repository to write files
        result = self.repo.write_task_queue(cell_dir, inp.project, inp.subproject, inp.cell, config)
        
        return WriteTaskQueueOutput(
            project=result.project,
            subproject=result.subproject,
            cell=result.cell,
            sis_task_queue_path=result.sis_task_queue_path,
            bytes_written_task_queue=result.bytes_written_task_queue,
            monte_carlo_settings_path=result.monte_carlo_settings_path,
            bytes_written_montecarlo=result.bytes_written_montecarlo,
            simulator=result.simulator,
            note=result.note,
        )


__all__ = [
    "GetTaskQueueStatus",
    "GetTaskQueueStatusInput",
    "GetTaskQueueStatusOutput",
    "WriteTaskQueue",
    "WriteTaskQueueInput",
    "WriteTaskQueueOutput",
]
