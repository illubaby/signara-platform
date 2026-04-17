"""Dependency factories for Post-Edit feature.
Adds new use-cases (cells & metrics) alongside existing SAF ones.
"""
from app.application.saf.post_edit_use_cases import (
    RunPostEdit,
    GetPostEditDefaults,
)
from app.application.post_edit.use_cases import (
    ListPostEditCells,
    GetPostEditMetrics,
)
from app.infrastructure.fs.post_edit_repository_fs import PostEditRepositoryFS

def _repo() -> PostEditRepositoryFS:
    # Simple factory – no caching needed yet.
    return PostEditRepositoryFS()

def get_run_post_edit_uc() -> RunPostEdit:
    return RunPostEdit()

def get_post_edit_defaults_uc() -> GetPostEditDefaults:
    return GetPostEditDefaults()

def get_list_post_edit_cells_uc() -> ListPostEditCells:
    return ListPostEditCells(_repo())

def get_post_edit_metrics_uc() -> GetPostEditMetrics:
    return GetPostEditMetrics(_repo())
