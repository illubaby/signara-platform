"""Pydantic schemas for Task Queue endpoints.

Maps between HTTP layer and domain entities.
"""
from pydantic import BaseModel
from typing import Optional


class TaskQueueRequestSchema(BaseModel):
    """Request schema for creating/updating task queue configuration."""
    normal_queue_no_prefix: str = "1"
    job_scheduler: str = "lsf"
    run_list_maxsize: str = "100"
    normal_queue: str = '-app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'
    statistical_montecarlo_sample_size: str = "250"
    netlist_max_sweeps: str = "1000"
    simulator: str = "primesim"
    statistical_simulation_points: str = "{1 3 5 7 9 11 13 15 17 19 21 23 25}"
    write_monte_carlo: bool = True


class TaskQueueResultSchema(BaseModel):
    """Response schema for task queue write result."""
    project: str
    subproject: str
    cell: str
    sis_task_queue_path: str
    bytes_written_task_queue: int
    monte_carlo_settings_path: Optional[str] = None
    bytes_written_montecarlo: Optional[int] = None
    simulator: str
    note: Optional[str] = None


class TaskQueueStatusSchema(BaseModel):
    """Response schema for task queue status."""
    project: str
    subproject: str
    cell: str
    exists_task_queue: bool
    exists_monte_carlo: bool
    values: TaskQueueRequestSchema
    simulator: str
    sis_task_queue_path: Optional[str] = None
    monte_carlo_settings_path: Optional[str] = None
    note: Optional[str] = None
