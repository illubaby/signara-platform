from __future__ import annotations

from pydantic import BaseModel
from typing import List


class ProjectListResponse(BaseModel):
    projects: List[str]


class SubprojectListResponse(BaseModel):
    project: str
    subprojects: List[str]
