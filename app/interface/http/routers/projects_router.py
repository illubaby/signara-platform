from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.interface.http.schemas.projects import ProjectListResponse, SubprojectListResponse
from app.interface.http.dependencies.projects import get_list_projects_uc, get_list_subprojects_uc
from app.application.projects.use_cases import ListProjects, ListSubprojects
from app.domain.common.validation import validate_component, ValidationError

router = APIRouter(prefix="/api", tags=["projects"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(list_uc: ListProjects = Depends(get_list_projects_uc)):
    return ProjectListResponse(projects=list_uc.execute())


@router.get("/projects/{project}/subprojects", response_model=SubprojectListResponse)
async def list_subprojects(project: str, list_uc: ListSubprojects = Depends(get_list_subprojects_uc)):
    _validate_component(project, "project")
    subprojects = list_uc.execute(project)
    if subprojects is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return SubprojectListResponse(project=project, subprojects=subprojects)

