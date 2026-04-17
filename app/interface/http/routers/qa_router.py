"""QA HTTP router - thin FastAPI endpoints."""
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import Optional

from app.interface.http.schemas.qa import (
    QACellListSchema, QACellSchema, QADefaultsSchema, QAChecksSchema,
    AvailableCellsSchema, RunQARequestSchema, RunQAResultSchema,
    QASummarySchema, QASummaryRowSchema, QAJobStatusSchema, CellCheckMatrixSchema
)
from app.application.qa.use_cases import (
    ListQACells, GetQADefaults, ListAvailableCells, RunQA,
    GetQASummary, GetQAJobStatus, ListQAChecks, GetQAMatrixSummary
)
from app.domain.qa.entities import QARunRequest
from app.domain.common.validation import validate_component, ValidationError


router = APIRouter(prefix="/api/qa", tags=["qa"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Dependency injection functions
def get_list_cells_uc() -> ListQACells:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return ListQACells(QARepositoryFS())


def get_defaults_uc() -> GetQADefaults:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return GetQADefaults(QARepositoryFS())


def get_available_cells_uc() -> ListAvailableCells:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return ListAvailableCells(QARepositoryFS())


def get_run_qa_uc() -> RunQA:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return RunQA(QARepositoryFS())


def get_summary_uc() -> GetQASummary:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return GetQASummary(QARepositoryFS())


def get_job_status_uc() -> GetQAJobStatus:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return GetQAJobStatus(QARepositoryFS())


def get_checks_uc() -> ListQAChecks:
    return ListQAChecks()


def get_matrix_summary_uc() -> GetQAMatrixSummary:
    from app.infrastructure.qa.qa_repository_fs import QARepositoryFS
    return GetQAMatrixSummary(QARepositoryFS())


# Endpoints
@router.get("/{project}/{subproject}/cells", response_model=QACellListSchema)
async def list_qa_cells(
    project: str,
    subproject: str,
    uc: ListQACells = Depends(get_list_cells_uc)
):
    """List all QA cells for a project/subproject."""
    for v, f in ((project, 'project'), (subproject, 'subproject')):
        _validate_component(v, f)
    
    cells = uc.execute(project, subproject)
    return QACellListSchema(
        project=project,
        subproject=subproject,
        cells=[QACellSchema(**c.__dict__) for c in cells],
        note=None if cells else "No QA cells found"
    )


@router.get("/{project}/{subproject}/defaults", response_model=QADefaultsSchema)
async def get_qa_defaults(
    project: str,
    subproject: str,
    cell: Optional[str] = Query(None),
    qa_type: str = Query('quality', description="QA type: 'quality' or 'process'"),
    uc: GetQADefaults = Depends(get_defaults_uc)
):
    """Get default parameters for QA execution."""
    for v, f in ((project, 'project'), (subproject, 'subproject')):
        _validate_component(v, f)
    if cell:
        _validate_component(cell, 'cell')
    
    defaults = uc.execute(project, subproject, cell, qa_type)
    return QADefaultsSchema(**defaults.__dict__)


@router.get("/{project}/{subproject}/checks", response_model=QAChecksSchema)
async def list_qa_checks(
    project: str,
    subproject: str,
    uc: ListQAChecks = Depends(get_checks_uc)
):
    """List available QA checks."""
    checks = uc.execute()
    return QAChecksSchema(checks=checks)


@router.get("/{project}/{subproject}/available-cells", response_model=AvailableCellsSchema)
async def list_available_cells(
    project: str,
    subproject: str,
    data_release: str = Query(...),
    uc: ListAvailableCells = Depends(get_available_cells_uc)
):
    """List available cells from data release directory."""
    for v, f in ((project, 'project'), (subproject, 'subproject')):
        _validate_component(v, f)
    
    cells = uc.execute(data_release)
    note = f"Found {len(cells)} cells" if cells else "No cell folders found"
    return AvailableCellsSchema(cells=cells, note=note)


@router.post("/{project}/{subproject}/run", response_model=RunQAResultSchema)
async def run_qa(
    project: str,
    subproject: str,
    req: RunQARequestSchema = Body(...),
    uc: RunQA = Depends(get_run_qa_uc)
):
    """Execute QA checks."""
    for v, f in ((project, 'project'), (subproject, 'subproject')):
        _validate_component(v, f)
    
    # Allow running without selected cells if a cell list file is provided
    if not req.selected_cells and not (req.cell_list_file and req.cell_list_file.strip()):
        raise HTTPException(status_code=400, detail="No cells selected and no cell_list_file provided")
    
    # Convert schema to domain entity
    domain_request = QARunRequest(
        selected_cells=req.selected_cells,
        data_release=req.data_release,
        header_file=req.header_file,
        cell_list_file=req.cell_list_file,
        project=req.project,
        release=req.release,
        plan_file=req.plan_file,
        outdir=req.outdir,
        queue=req.queue,
        run_dir=req.run_dir,
        selected_checks=req.selected_checks
    )
    
    result = uc.execute(project, subproject, domain_request)
    return RunQAResultSchema(**result.__dict__)


@router.get("/{project}/{subproject}/summary", response_model=QASummarySchema)
async def get_qa_summary(
    project: str,
    subproject: str,
    cell: str = Query(...),
    uc: GetQASummary = Depends(get_summary_uc)
):
    """Get QA summary for a cell."""
    for v, f in ((project, 'project'), (subproject, 'subproject'), (cell, 'cell')):
        _validate_component(v, f)
    
    summary = uc.execute(project, subproject, cell)
    return QASummarySchema(
        project=summary.project,
        subproject=summary.subproject,
        cell=summary.cell,
        rows=[QASummaryRowSchema(**r.__dict__) for r in summary.rows],
        source=summary.source,
        note=f"{len(summary.rows)} rows" if summary.rows else "No summary data"
    )


@router.get("/job/{job_id}", response_model=QAJobStatusSchema)
async def get_job_status(
    job_id: str,
    uc: GetQAJobStatus = Depends(get_job_status_uc)
):
    """Get status of a running QA job."""
    status = uc.execute(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return QAJobStatusSchema(**status.__dict__)


@router.get("/{project}/{subproject}/matrix-summary", response_model=CellCheckMatrixSchema)
async def get_matrix_summary(
    project: str,
    subproject: str,
    run_dir: str = Query(..., description="Run directory containing cell folders with brief.sum files"),
    uc: GetQAMatrixSummary = Depends(get_matrix_summary_uc)
):
    """Get QA matrix summary from brief.sum files (check items × cells)."""
    for v, f in ((project, 'project'), (subproject, 'subproject')):
        _validate_component(v, f)
    
    matrix = uc.execute(project, subproject, run_dir)
    
    note = f"{len(matrix.check_items)} checks × {len(matrix.cell_names)} cells"
    if matrix.cells_with_brief_sum:
        note += f" ({len(matrix.cells_with_brief_sum)} with brief.sum)"
    
    return CellCheckMatrixSchema(
        project=matrix.project,
        subproject=matrix.subproject,
        run_dir=matrix.run_dir,
        cell_names=matrix.cell_names,
        check_items=matrix.check_items,
        status_matrix=matrix.status_matrix,
        cells_with_brief_sum=matrix.cells_with_brief_sum,
        missing_cells=matrix.missing_cells,
        note=note
    )

