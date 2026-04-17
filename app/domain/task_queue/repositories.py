"""Task Queue repository protocol (port).

Defines the interface for task queue persistence operations.
"""
from pathlib import Path
from typing import Protocol
from app.domain.task_queue.entities import TaskQueueConfig, TaskQueueResult, TaskQueueStatus


class TaskQueueRepository(Protocol):
    """Repository for managing task queue configuration files."""
    
    def write_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str,
        config: TaskQueueConfig
    ) -> TaskQueueResult:
        """Write task queue configuration files to cell directory.
        
        Creates:
        - sis_task_queue.tcl (always)
        - monte_carlo_settings.tcl (if config.write_monte_carlo is True)
        
        Args:
            cell_dir: Cell directory path
            project: Project name
            subproject: Subproject name
            cell: Cell name
            config: Task queue configuration
            
        Returns:
            TaskQueueResult with paths and bytes written
            
        Raises:
            RuntimeError: If file write fails
        """
        ...
    
    def read_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str
    ) -> TaskQueueStatus:
        """Read existing task queue configuration from cell directory.
        
        Args:
            cell_dir: Cell directory path
            project: Project name
            subproject: Subproject name
            cell: Cell name
            
        Returns:
            TaskQueueStatus with existing configuration or defaults
        """
        ...
