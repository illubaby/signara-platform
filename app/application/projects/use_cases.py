from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Protocol
import time

from app.domain.projects.repositories import ProjectRepository


class Cache(Protocol):  # minimal protocol for alternative injection later
    def get(self, key: str): ...
    def set(self, key: str, value, ttl: int): ...


class SimpleTTLCache:
    def __init__(self):
        self._store: Dict[str, Tuple[float, object]] = {}

    def get(self, key: str):
        item = self._store.get(key)
        if not item:
            return None
        expiry, value = item
        if time.time() > expiry:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value, ttl: int):
        self._store[key] = (time.time() + ttl, value)


@dataclass
class ListProjects:
    repo: ProjectRepository
    cache: Cache = field(default_factory=SimpleTTLCache)
    ttl: int = 30

    def execute(self) -> List[str]:
        key = "projects"
        cached = self.cache.get(key)
        if cached is not None:
            return cached  # type: ignore
        projects = self.repo.list_projects()
        self.cache.set(key, projects, self.ttl)
        return projects


@dataclass
class ListSubprojects:
    repo: ProjectRepository
    cache: Cache = field(default_factory=SimpleTTLCache)
    ttl: int = 30

    def execute(self, project: str) -> List[str]:
        key = f"subprojects:{project}"
        cached = self.cache.get(key)
        if cached is not None:
            return cached  # type: ignore
        subprojects = self.repo.list_subprojects(project)
        self.cache.set(key, subprojects, self.ttl)
        return subprojects
@dataclass
class GetConstraintPath:
    def execute(self, project: str) -> str:
        p = project.lower().strip()
        if p.startswith("h1"):
            return "//wwcad/msip/projects/ucie/tb/gr_ucie/design/timing/plan/uciephy_constraint.xlsx"
        if p.startswith("h2"):
            return "//wwcad/msip/projects/ucie/tb/gr_ucie2_v2/design/timing/plan/uciephy_constraint.xlsx"
        if p.startswith("h3"):
            return "//wwcad/msip/projects/ucie/tb/gr_ucie3_v1/design/timing/plan/uciephy_constraint.xlsx"
        raise ValueError("Unsupported project prefix for constraint path")