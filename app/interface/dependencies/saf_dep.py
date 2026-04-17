"""FastAPI dependency providers for SAF use-cases (Phase 5).

Centralizes construction of repositories and use-case instances so routers
no longer instantiate infrastructure classes directly. This supports
protocol-based decoupling and future mocking.
"""
from __future__ import annotations
from functools import lru_cache

from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
from app.infrastructure.fs.pvt_status_repository_fs import PvtStatusRepositoryFS
from app.infrastructure.fs.symlink_service import SymlinkService
from app.infrastructure.processes.job_execution_service import JobExecutionService

from app.application.saf.list_and_diagnose_use_cases import (
    ListSafCells, ListSafCellsInput, DiagnoseSaf
)
from app.application.saf.pre_run_use_cases import (
    EnsureCellDirectories, EnsureCellConfig, EnsureNetlistPresent
)
from app.application.saf.symlink_use_cases import EnsureSafSymlinks
from app.application.saf.job_script_use_cases import GenerateJobScript, RunJobScript
from app.application.saf.prepare_run_use_case import PrepareAndRunJob
from app.application.saf.netlist_use_cases import SyncNetlist, GetNetlistDebug
from app.application.saf.use_cases import GetPvtStatuses
from app.application.saf.saf_library_use_cases import (
    CountPosteditLibs, CountPosteditLibsInput,
    CountPostqaLibs, CountPostqaLibsInput,
)
from app.application.saf.post_edit_use_cases import (
    GetPostEditDefaults, RunPostEdit
)
from app.application.saf.pvt_use_cases import (
    GetPvtList, GetNtPvtList
)
from app.application.saf.task_queue_use_cases import GetTaskQueueStatus, WriteTaskQueue
from app.application.saf.file_operations_use_cases import (
    ListPvtFiles, ReadPvtFile, WritePvtFile
)
from app.application.saf.sync_use_cases import CheckAndSyncInstFile
from app.application.saf.ttl_cache import TTLCache
from app.infrastructure.settings.settings import get_settings

@lru_cache
def _cache() -> TTLCache:
    return TTLCache(ttl_seconds=get_settings().cache_ttl_seconds)

@lru_cache
def cell_repo() -> SafCellRepositoryFS:
    return SafCellRepositoryFS()

@lru_cache
def perforce_repo() -> SafPerforceRepositoryP4:
    return SafPerforceRepositoryP4()

@lru_cache
def status_repo() -> PvtStatusRepositoryFS:
    return PvtStatusRepositoryFS()

@lru_cache
def symlink_service() -> SymlinkService:
    return SymlinkService()

@lru_cache
def exec_service() -> JobExecutionService:
    return JobExecutionService()

# Use-case factories

def list_saf_cells_uc() -> ListSafCells:
    return ListSafCells(cell_repo(), perforce_repo(), _cache())

def diagnose_saf_uc() -> DiagnoseSaf:
    return DiagnoseSaf(cell_repo())

def ensure_dirs_uc() -> EnsureCellDirectories:
    return EnsureCellDirectories(cell_repo())

def ensure_cfg_uc() -> EnsureCellConfig:
    return EnsureCellConfig(perforce_repo())

def ensure_net_uc() -> EnsureNetlistPresent:
    return EnsureNetlistPresent(perforce_repo())

def ensure_symlinks_uc() -> EnsureSafSymlinks:
    return EnsureSafSymlinks(symlink_service())

def generate_job_script_uc() -> GenerateJobScript:
    return GenerateJobScript()

def run_job_script_uc() -> RunJobScript:
    return RunJobScript(exec_service())

def prepare_and_run_job_uc() -> PrepareAndRunJob:
    return PrepareAndRunJob(exec_service(), ensure_dirs_uc(), ensure_cfg_uc(), ensure_net_uc(), ensure_symlinks_uc(), generate_job_script_uc(), run_job_script_uc())

def get_pvt_statuses_uc() -> GetPvtStatuses:
    return GetPvtStatuses(status_repo())

def sync_netlist_uc() -> SyncNetlist:
    return SyncNetlist(perforce_repo())

def get_netlist_debug_uc() -> GetNetlistDebug:
    return GetNetlistDebug(cell_repo())

def count_postedit_libs_uc() -> CountPosteditLibs:
    return CountPosteditLibs()

def count_postqa_libs_uc() -> CountPostqaLibs:
    return CountPostqaLibs()

def get_postedit_defaults_uc() -> GetPostEditDefaults:
    return GetPostEditDefaults()

def run_postedit_uc() -> RunPostEdit:
    return RunPostEdit()

def get_pvt_list_uc() -> GetPvtList:
    return GetPvtList(perforce_repo())

def get_nt_pvt_list_uc() -> GetNtPvtList:
    return GetNtPvtList(cell_repo())

def get_task_queue_status_uc() -> GetTaskQueueStatus:
    return GetTaskQueueStatus(cell_repo())

def write_task_queue_uc() -> WriteTaskQueue:
    return WriteTaskQueue(cell_repo())

def list_pvt_files_uc() -> ListPvtFiles:
    return ListPvtFiles(cell_repo())

def read_pvt_file_uc() -> ReadPvtFile:
    return ReadPvtFile(cell_repo())

def write_pvt_file_uc() -> WritePvtFile:
    return WritePvtFile(cell_repo())

def check_and_sync_inst_file_uc() -> CheckAndSyncInstFile:
    return CheckAndSyncInstFile(cell_repo(), perforce_repo())

__all__ = [
    "list_saf_cells_uc", "diagnose_saf_uc", "prepare_and_run_job_uc",
    "get_pvt_statuses_uc", "sync_netlist_uc", "get_netlist_debug_uc",
    "count_postedit_libs_uc", "count_postqa_libs_uc",
    "get_postedit_defaults_uc", "run_postedit_uc",
    "get_pvt_list_uc", "get_nt_pvt_list_uc", "get_task_queue_status_uc",
    "list_pvt_files_uc", "read_pvt_file_uc", "write_pvt_file_uc",
    "check_and_sync_inst_file_uc",
    "perforce_repo", "cell_repo",
]
