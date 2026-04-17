from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    name: str

    def __post_init__(self):
        if not self.name or '/' in self.name or '..' in self.name:
            raise ValueError("Invalid project name")


@dataclass(frozen=True)
class Subproject:
    project: str
    name: str

    def __post_init__(self):
        if not self.project or not self.name:
            raise ValueError("Invalid subproject")
        for part in (self.project, self.name):
            if '/' in part or '..' in part:
                raise ValueError("Invalid subproject path component")
