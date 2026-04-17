from __future__ import annotations

from functools import lru_cache

from app.application.projects.use_cases import ListProjects, ListSubprojects
from app.infrastructure.fs.project_repo_fs import ProjectRepositoryFS


@lru_cache
def get_list_projects_uc() -> ListProjects:
    repo = ProjectRepositoryFS()
    return ListProjects(repo)


@lru_cache
def get_list_subprojects_uc() -> ListSubprojects:
    repo = ProjectRepositoryFS()
    return ListSubprojects(repo)
