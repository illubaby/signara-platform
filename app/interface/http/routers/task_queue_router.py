"""Generic Task Queue router.

Exposes endpoints for managing sis_task_queue.tcl and monte_carlo_settings.tcl files.
Follows Clean Architecture - thin adapter layer over use cases.
"""
from fastapi import APIRouter, HTTPException, Body, Depends
from app.domain.common.validation import validate_component, ValidationError
from app.interface.http.schemas.task_queue import (
    TaskQueueRequestSchema,
    TaskQueueResultSchema,
    TaskQueueStatusSchema
)
from app.application.task_queue.use_cases import (
    WriteTaskQueue,
    WriteTaskQueueInput,
    GetTaskQueueStatus,
    GetTaskQueueStatusInput
)
from app.domain.task_queue.entities import TaskQueueConfig
from app.interface.http.dependencies import get_write_task_queue_uc, get_task_queue_status_uc

router = APIRouter(prefix="/api/taskqueue", tags=["task-queue"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project}/{subproject}/{cell}", response_model=TaskQueueResultSchema)
async def create_task_queue(
    project: str,
    subproject: str,
    cell: str,
    req: TaskQueueRequestSchema = Body(...),
    write_uc: WriteTaskQueue = Depends(get_write_task_queue_uc)
):
    """Create or update task queue configuration for a cell."""
    for value, field in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(value, field)
    
    try:
        config = TaskQueueConfig(
            normal_queue_no_prefix=req.normal_queue_no_prefix,
            job_scheduler=req.job_scheduler,
            run_list_maxsize=req.run_list_maxsize,
            normal_queue=req.normal_queue,
            statistical_montecarlo_sample_size=req.statistical_montecarlo_sample_size,
            netlist_max_sweeps=req.netlist_max_sweeps,
            simulator=req.simulator,
            statistical_simulation_points=req.statistical_simulation_points,
            write_monte_carlo=req.write_monte_carlo
        )
        
        inp = WriteTaskQueueInput(
            project=project,
            subproject=subproject,
            cell=cell,
            config=config
        )
        result = write_uc.execute(inp)
        
        return TaskQueueResultSchema(
            project=result.project,
            subproject=result.subproject,
            cell=result.cell,
            sis_task_queue_path=result.sis_task_queue_path,
            bytes_written_task_queue=result.bytes_written_task_queue,
            monte_carlo_settings_path=result.monte_carlo_settings_path,
            bytes_written_montecarlo=result.bytes_written_montecarlo,
            simulator=result.simulator,
            note=result.note
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project}/{subproject}/{cell}", response_model=TaskQueueStatusSchema)
async def get_task_queue(
    project: str,
    subproject: str,
    cell: str,
    status_uc: GetTaskQueueStatus = Depends(get_task_queue_status_uc)
):
    """Get task queue configuration status for a cell."""
    for value, field in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(value, field)
    
    try:
        inp = GetTaskQueueStatusInput(
            project=project,
            subproject=subproject,
            cell=cell
        )
        status = status_uc.execute(inp)
        
        values_schema = TaskQueueRequestSchema(
            normal_queue_no_prefix=status.config.normal_queue_no_prefix,
            job_scheduler=status.config.job_scheduler,
            run_list_maxsize=status.config.run_list_maxsize,
            normal_queue=status.config.normal_queue,
            statistical_montecarlo_sample_size=status.config.statistical_montecarlo_sample_size,
            netlist_max_sweeps=status.config.netlist_max_sweeps,
            simulator=status.config.simulator,
            statistical_simulation_points=status.config.statistical_simulation_points,
            write_monte_carlo=status.config.write_monte_carlo
        )
        
        return TaskQueueStatusSchema(
            project=status.project,
            subproject=status.subproject,
            cell=status.cell,
            exists_task_queue=status.exists_task_queue,
            exists_monte_carlo=status.exists_monte_carlo,
            values=values_schema,
            simulator=status.simulator,
            sis_task_queue_path=status.sis_task_queue_path,
            monte_carlo_settings_path=status.monte_carlo_settings_path,
            note=status.note
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

