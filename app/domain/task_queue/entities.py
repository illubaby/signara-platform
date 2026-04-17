"""Task Queue domain entities.

Pure domain models representing task queue configuration and status.
No external dependencies - only standard library.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TaskQueueConfig:
    """Task queue configuration for timing simulation."""
    
    normal_queue_no_prefix: str = "1"
    job_scheduler: str = "lsf"
    run_list_maxsize: str = "100"
    normal_queue: str = '-app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"'
    statistical_montecarlo_sample_size: str = "250"
    netlist_max_sweeps: str = "1000"
    simulator: str = "primesim"
    # TCL list for statistical simulation points; keep braces to preserve spaces
    statistical_simulation_points: str = "{1 3 5 7 9 11 13 15 17 19 21 23 25}"
    write_monte_carlo: bool = True


@dataclass(frozen=True)
class TaskQueueResult:
    """Result of writing task queue files."""
    
    project: str
    subproject: str
    cell: str
    sis_task_queue_path: str
    bytes_written_task_queue: int
    monte_carlo_settings_path: Optional[str]
    bytes_written_montecarlo: Optional[int]
    simulator: str
    note: Optional[str] = None


@dataclass(frozen=True)
class TaskQueueStatus:
    """Status of existing task queue configuration."""
    
    project: str
    subproject: str
    cell: str
    exists_task_queue: bool
    exists_monte_carlo: bool
    config: TaskQueueConfig
    simulator: str
    sis_task_queue_path: Optional[str]
    monte_carlo_settings_path: Optional[str]
    note: Optional[str] = None
