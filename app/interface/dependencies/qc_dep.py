"""Dependency injection factories for QC use cases.

Provides singleton instances of use cases with their dependencies properly wired.
"""

from typing import Dict, Any
from app.application.qc.use_cases import CreateTaskQueue, GetTaskQueue
from app.application.qc.list_cells_use_case import ListCellsUseCase
from app.application.qc.get_defaults_use_case import GetDefaultsUseCase
from app.application.qc.list_testbenches_use_case import ListTestbenchesUseCase
from app.application.qc.get_important_arcs_use_case import GetImportantArcsUseCase
from app.application.qc.get_testbench_status_use_case import GetTestbenchStatusUseCase
from app.application.qc.generate_qc_table_use_case import GenerateQCTableUseCase
from app.infrastructure.qc.task_queue_repository_fs import TaskQueueRepositoryFS
from app.infrastructure.qc.cell_repository_fs import QCCellRepositoryFS
from app.infrastructure.qc.p4v_repository import QCP4VRepositoryP4
from app.infrastructure.qc.default_paths_repository import DefaultPathsRepositoryFS
from app.infrastructure.qc.testbench_repository_fs import TestbenchRepositoryFS


# Singleton instances
_task_queue_repo = None
_create_task_queue_uc = None
_get_task_queue_uc = None
_cell_repo = None
_p4v_repo = None
_list_cells_uc = None
_defaults_repo = None
_get_defaults_uc = None
_testbench_repo = None
_list_testbenches_uc = None
_get_important_arcs_uc = None
_get_testbench_status_uc = None
_generate_qc_table_uc = None

# Global cache for QC data (shared across use cases)
_global_cache: Dict[str, Dict[str, Any]] = {}


def get_task_queue_repository() -> TaskQueueRepositoryFS:
    """Get singleton task queue repository."""
    global _task_queue_repo
    if _task_queue_repo is None:
        _task_queue_repo = TaskQueueRepositoryFS()
    return _task_queue_repo


def get_create_task_queue_use_case() -> CreateTaskQueue:
    """Get singleton CreateTaskQueue use case."""
    global _create_task_queue_uc
    if _create_task_queue_uc is None:
        _create_task_queue_uc = CreateTaskQueue(get_task_queue_repository())
    return _create_task_queue_uc


def get_get_task_queue_use_case() -> GetTaskQueue:
    """Get singleton GetTaskQueue use case."""
    global _get_task_queue_uc
    if _get_task_queue_uc is None:
        _get_task_queue_uc = GetTaskQueue(get_task_queue_repository())
    return _get_task_queue_uc


def get_cell_repository() -> QCCellRepositoryFS:
    """Get singleton cell repository."""
    global _cell_repo
    if _cell_repo is None:
        _cell_repo = QCCellRepositoryFS()
    return _cell_repo


def get_p4v_repository() -> QCP4VRepositoryP4:
    """Get singleton P4V repository."""
    global _p4v_repo
    if _p4v_repo is None:
        _p4v_repo = QCP4VRepositoryP4()
    return _p4v_repo


def get_list_cells_use_case() -> ListCellsUseCase:
    """Get singleton ListCells use case."""
    global _list_cells_uc
    if _list_cells_uc is None:
        _list_cells_uc = ListCellsUseCase(
            get_cell_repository(),
            get_p4v_repository(),
            _global_cache
        )
    return _list_cells_uc


def get_defaults_repository() -> DefaultPathsRepositoryFS:
    """Get singleton defaults repository."""
    global _defaults_repo
    if _defaults_repo is None:
        _defaults_repo = DefaultPathsRepositoryFS()
    return _defaults_repo


def get_defaults_use_case() -> GetDefaultsUseCase:
    """Get singleton GetDefaults use case."""
    global _get_defaults_uc
    if _get_defaults_uc is None:
        _get_defaults_uc = GetDefaultsUseCase(get_defaults_repository())
    return _get_defaults_uc


def get_testbench_repository() -> TestbenchRepositoryFS:
    """Get singleton testbench repository."""
    global _testbench_repo
    if _testbench_repo is None:
        _testbench_repo = TestbenchRepositoryFS()
    return _testbench_repo


def get_list_testbenches_use_case() -> ListTestbenchesUseCase:
    """Get singleton ListTestbenches use case."""
    global _list_testbenches_uc
    if _list_testbenches_uc is None:
        _list_testbenches_uc = ListTestbenchesUseCase(get_testbench_repository())
    return _list_testbenches_uc


def get_important_arcs_use_case() -> GetImportantArcsUseCase:
    """Get singleton GetImportantArcs use case."""
    global _get_important_arcs_uc
    if _get_important_arcs_uc is None:
        _get_important_arcs_uc = GetImportantArcsUseCase()
    return _get_important_arcs_uc


def get_testbench_status_use_case() -> GetTestbenchStatusUseCase:
    """Get singleton GetTestbenchStatus use case."""
    global _get_testbench_status_uc
    if _get_testbench_status_uc is None:
        _get_testbench_status_uc = GetTestbenchStatusUseCase()
    return _get_testbench_status_uc


def get_generate_qc_table_use_case() -> GenerateQCTableUseCase:
    """Get singleton GenerateQCTable use case."""
    global _generate_qc_table_uc
    if _generate_qc_table_uc is None:
        _generate_qc_table_uc = GenerateQCTableUseCase(
            get_testbench_repository(),
            _global_cache
        )
    return _generate_qc_table_uc
