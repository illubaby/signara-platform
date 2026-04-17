from __future__ import annotations

from pathlib import Path
from typing import List, Iterable, Set

from app.domain.projects.repositories import ProjectRepository
from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR

# Additional source of projects/subprojects to merge with BASE_DIR.
# Do not introduce a new base resolution; only read if path exists.
CAD_REP_BASE = Path("/remote/cad-rep/projects/ucie")


def _list_dir_names(parent: Path) -> List[str]:
    if not parent.exists() or not parent.is_dir():
        return []
    names: List[str] = []
    for entry in parent.iterdir():
        if entry.is_dir() and not entry.name.startswith('.'):
            names.append(entry.name)
    return sorted(names, key=str.lower)


def _merge_unique(*lists: Iterable[str]) -> List[str]:
    seen: Set[str] = set()
    merged: List[str] = []
    for lst in lists:
        for name in lst:
            if name not in seen:
                seen.add(name)
                merged.append(name)
    return sorted(merged, key=str.lower)


class ProjectRepositoryFS(ProjectRepository):  # type: ignore[misc]
    def list_projects(self) -> List[str]:  # pragma: no cover - simple IO
        base_projects = _list_dir_names(BASE_DIR)
        cad_rep_projects = _list_dir_names(CAD_REP_BASE)
        return _merge_unique(base_projects, cad_rep_projects)

    def list_subprojects(self, project: str) -> List[str]:  # pragma: no cover - simple IO
        base_sub = _list_dir_names(BASE_DIR / project)
        cad_rep_sub = _list_dir_names(CAD_REP_BASE / project)
        return _merge_unique(base_sub, cad_rep_sub)
