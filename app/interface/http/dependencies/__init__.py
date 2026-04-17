from app.application.lsf.use_cases import RunBjobs
from app.infrastructure.processes.lsf_jobs_runner import SubprocessLSFJobRunner
from app.application.task_queue.use_cases import WriteTaskQueue, GetTaskQueueStatus
from app.infrastructure.fs.task_queue_repository_fs import TaskQueueRepositoryFS
from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS

def get_run_bjobs_uc() -> RunBjobs:
    return RunBjobs(SubprocessLSFJobRunner())

def get_write_task_queue_uc() -> WriteTaskQueue:
    return WriteTaskQueue(
        task_queue_repo=TaskQueueRepositoryFS(),
        cell_repo=SafCellRepositoryFS()
    )

def get_task_queue_status_uc() -> GetTaskQueueStatus:
    return GetTaskQueueStatus(
        task_queue_repo=TaskQueueRepositoryFS(),
        cell_repo=SafCellRepositoryFS()
    )

__all__ = ["get_run_bjobs_uc", "get_write_task_queue_uc", "get_task_queue_status_uc"]