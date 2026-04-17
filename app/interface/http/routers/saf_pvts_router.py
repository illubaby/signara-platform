"""Dedicated SAF PVT-related router.

Extracted from original saf_router to reduce file size and isolate PVT concerns.

Endpoints:
  GET /api/saf/{project}/{subproject}/pvts
  GET /api/saf/{project}/{subproject}/cells/{cell}/nt-pvts
  GET /api/saf/{project}/{subproject}/cells/{cell}/pvt-status

All validation performed via domain validation; no business logic here.
"""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from app.interface.http.schemas.saf import PVTListResponse, PVTStatusResponse
from app.application.saf.pvt_use_cases import (
	GetPvtList, GetPvtListInput,
	GetNtPvtList, GetNtPvtListInput,
)
from app.application.saf.use_cases import (
	GetPvtStatuses, GetPvtStatusesInput,
)
from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS
from app.domain.common.validation import validate_component, ValidationError

router = APIRouter(prefix="/api/saf", tags=["saf-pvts"])


def _validate_component(name: str, field: str = "component") -> None:
	try:
		validate_component(name, field)
	except ValidationError as e:
		raise HTTPException(status_code=400, detail=str(e))


def get_pvt_list_uc() -> GetPvtList:
	from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4
	return GetPvtList(SafPerforceRepositoryP4())


def get_nt_pvt_list_uc() -> GetNtPvtList:
	return GetNtPvtList(SafCellRepositoryFS())


def get_pvt_statuses_uc() -> GetPvtStatuses:
	from app.infrastructure.fs.pvt_status_repository_fs import PvtStatusRepositoryFS
	return GetPvtStatuses(PvtStatusRepositoryFS())


@router.get("/{project}/{subproject}/pvts", response_model=PVTListResponse)
async def get_pvt_list(
	project: str,
	subproject: str,
	internal: bool = Query(False, description="Use internal SAF configure_pvt.tcl"),
	uc: GetPvtList = Depends(get_pvt_list_uc)
):
	for v, f in ((project, "project"), (subproject, "subproject")):
		_validate_component(v, f)
	try:
		out = uc.execute(GetPvtListInput(project=project, subproject=subproject, internal=internal))
		return PVTListResponse(project=project, subproject=subproject, pvts=out.pvts, note=out.note)
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project}/{subproject}/cells/{cell}/nt-pvts", response_model=PVTListResponse)
async def get_nt_pvt_list(
	project: str,
	subproject: str,
	cell: str,
	uc: GetNtPvtList = Depends(get_nt_pvt_list_uc)
):
	for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
		_validate_component(v, f)
	try:
		out = uc.execute(GetNtPvtListInput(project=project, subproject=subproject, cell=cell))
		return PVTListResponse(project=project, subproject=subproject, pvts=out.pvts, note=out.note)
	except ValueError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project}/{subproject}/cells/{cell}/pvt-status", response_model=PVTStatusResponse)
async def get_pvt_status(
	project: str,
	subproject: str,
	cell: str,
	cell_type: str = Query("sis", description="Cell type: 'sis' or 'nt'"),
	uc: GetPvtStatuses = Depends(get_pvt_statuses_uc)
):
	for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
		_validate_component(v, f)
	repo = SafCellRepositoryFS()
	is_nt = (cell_type == "nt")
	root = repo.resolve_nt_root(project, subproject) if is_nt else repo.resolve_sis_root(project, subproject)
	root_desc = "NT directory" if is_nt else "SiS directory"
	if not root:
		raise HTTPException(status_code=404, detail=f"{root_desc} not found")
	from pathlib import Path as _P
	cell_dir = _P(root) / cell
	if not cell_dir.exists():
		raise HTTPException(status_code=404, detail=f"Cell directory not found: {cell}")
	out = uc.execute(GetPvtStatusesInput(cell_dir=str(cell_dir), is_nt=is_nt))
	return PVTStatusResponse(project=project, subproject=subproject, cell=cell, statuses=out.statuses, summary=out.summary)


__all__ = ["router"]
