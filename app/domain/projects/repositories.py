from __future__ import annotations

from typing import Protocol, List


class ProjectRepository(Protocol):  # pragma: no cover - protocol definition
    def list_projects(self) -> List[str]: ...
    def list_subprojects(self, project: str) -> List[str]: ...
