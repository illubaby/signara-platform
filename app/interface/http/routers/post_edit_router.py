from fastapi import APIRouter, HTTPException, Body, Query, Depends, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pathlib import Path
from typing import Optional, List

from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
from app.domain.common.validation import validate_component, ValidationError
from app.infrastructure.fs.post_edit_repository_fs import quality_base  # migrated
from app.application.saf.post_edit_use_cases import (
    GetPostEditDefaults, GetPostEditDefaultsInput,
    RunPostEdit, RunPostEditInput,
)
from app.infrastructure.fs.symlink_service import SymlinkService
from app.infrastructure.websocket.stream_executor import WebSocketStreamExecutor

from app.interface.http.schemas.post_edit import (
    ConfigSaveRequest, ConfigSaveResult,
    PostEditCell, PostEditCellList, PostEditDefaults,
    CellMetric, PostEditMetrics,
)
from app.interface.http.dependencies.post_edit import (
    get_post_edit_defaults_uc,
    get_list_post_edit_cells_uc, get_post_edit_metrics_uc,
)

router = APIRouter(prefix="/api/post-edit", tags=["timing-post-edit"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config", response_model=ConfigSaveResult)
async def save_config(req: ConfigSaveRequest):
    p = Path(req.path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(req.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write config: {e}")
    return ConfigSaveResult(path=str(p), bytes_written=p.stat().st_size, note="saved")

@router.get("/config")
async def read_config(path: str):
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Config file not found")
    try:
        return {"path": str(p), "content": p.read_text()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read config: {e}")


@router.get("/{project}/{subproject}/cells", response_model=PostEditCellList)
async def list_post_edit_cells(
    project: str,
    subproject: str,
    debug: bool = Query(False),
    include_missing: bool = Query(False),
    list_cells_uc = Depends(get_list_post_edit_cells_uc),
):
    for comp, field in ((project, "project"), (subproject, "subproject")):
        _validate_component(comp, field)
    base_dir = quality_base(project, subproject)
    config_dir = base_dir / "config"
    meta_cells = list_cells_uc.execute(project, subproject, include_missing=include_missing)
    filtered = meta_cells  # already filtered by use-case
    cells = [PostEditCell(cell=m.cell, config_path=m.config_path, exists=m.exists) for m in filtered]
    note = None
    if not config_dir.exists() and debug:
        note = f"Config directory missing: {config_dir}"
    return PostEditCellList(
        project=project,
        subproject=subproject,
        base_dir=str(base_dir),
        config_dir=str(config_dir),
        cells=cells,
        note=note
    )

@router.get("/{project}/{subproject}/defaults", response_model=PostEditDefaults)
async def post_edit_defaults(
    project: str,
    subproject: str,
    cell: Optional[str] = None,
    defaults_uc: GetPostEditDefaults = Depends(get_post_edit_defaults_uc),
):
    for comp, field in ((project, "project"), (subproject, "subproject")):
        _validate_component(comp, field)
    base_dir = quality_base(project, subproject)
    meta = defaults_uc.execute(GetPostEditDefaultsInput(project=project, subproject=subproject, cell=cell))
    return PostEditDefaults(
        project=project,
        subproject=subproject,
        cell=cell,
        base_dir=str(base_dir),
        config_dir=meta.config_dir,
        config_file=meta.config_file,
        lib_path=meta.lib_path,
        reference_path=meta.reference_path,
        output_path=meta.output_path,
        note=None,
    )

@router.get("/{project}/{subproject}/metrics", response_model=PostEditMetrics)
async def post_edit_metrics(
    project: str,
    subproject: str,
    lib_path: Optional[str] = None,
    include_missing: bool = Query(False),
    metrics_uc = Depends(get_post_edit_metrics_uc),
):
    for comp, field in ((project, "project"), (subproject, "subproject")):
        _validate_component(comp, field)
    meta_metrics = metrics_uc.execute(project, subproject, lib_path=lib_path, include_missing=include_missing)
    metrics = [CellMetric(cell=m.cell, aLibs_count=m.a_libs_count, updated_libs_count=m.updated_libs_count, complete=m.complete)
               for m in meta_metrics]
    return PostEditMetrics(project=project, subproject=subproject, cells=metrics)


# ======================== WebSocket Streaming Endpoint ========================
# Provides real-time (incremental) execution for Post-Edit runs using the
# shared WebSocketStreamExecutor infrastructure component. Mirrors logic in the
# synchronous POST /run endpoint (command construction + symlink setup) but
# streams stdout live and supports client stop signal.

@router.websocket("/{project}/{subproject}/run/ws")
async def run_post_edit_stream(
    websocket: WebSocket,
    project: str,
    subproject: str,
    cell: str = Query(..., description="Cell name"),
    configfile: str = Query(..., description="Full path to cell .cfg file"),
    lib: str | None = Query(None, description="Library path (optional)"),
    plan: str | None = Query(None, description="Constraint plan path (optional)"),
    reformat: str | None = Query(None, description="Reformat mode (pt|sis)"),
    pt: str = Query(..., description="PT binary or path"),
    output: str | None = Query(None, description="Optional output directory"),
    reference: str | None = Query(None, description="Optional reference directory"),
    copy_reference: bool = Query(False, description="Copy reference libs"),
    reorder: bool = Query(False, description="Enable reorder flag"),
    leakage: bool = Query(False, description="Enable leakage flag"),
    update: bool = Query(False, description="Enable update flag"),
):
    """WebSocket live execution for Post-Edit.

    Query parameters mirror the JSON body of the synchronous /run endpoint.

    WebSocket Protocol:
      Client → Server: {"action": "stop"} to terminate execution
      Server → Client (from infrastructure executor):
        {"stream": "stdout", "data": "line"}
        {"event": "error", "detail": "message"}
        {"event": "end", "return_code": 0, "stopped": false}

    This endpoint performs the same symlink setup as the POST endpoint and
    injects those messages at start for visibility.
    """
    await websocket.accept()

    # Validate identifiers
    try:
        for comp, field in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
            _validate_component(comp, field)
    except HTTPException as e:
        # Send validation failure then close
        try:
            await websocket.send_json({"event": "error", "detail": e.detail})
            await websocket.close()
        except Exception:
            pass
        return

    # Build command using use case (Clean Architecture: delegate to application layer)
    # This now generates runall.csh script in the quality directory
    use_case = RunPostEdit()
    try:
        cmd_parts, quality_dir, script_path = use_case.build_command(RunPostEditInput(
            project=project,
            subproject=subproject,
            cell=cell,
            configfile=configfile,
            lib=lib,
            plan=plan,
            reformat=reformat,
            pt=pt,
            output=output,
            reference=reference,
            copy_reference=copy_reference,
            reorder=reorder,
            leakage=leakage,
            update=update,
        ))
    except (FileNotFoundError, ValueError) as e:
        try:
            await websocket.send_json({"event": "error", "detail": str(e)})
            await websocket.close()
        except Exception:
            pass
        return

    # Symlink setup (reuse logic but send as setup messages)
    setup_messages: list[str] = []
    try:
        symlink_service = SymlinkService()
        link_res = symlink_service.link_cell_tools(quality_dir)
        decorated = [f"[Symlink] {l}" for l in (link_res.results + link_res.warnings)]
        setup_messages.extend(decorated)
        if link_res.note:
            setup_messages.append(f"[Symlink Note] {link_res.note}")
    except Exception as e:
        setup_messages.append(f"[Symlink Error] {e}")

    setup_messages.append(f"[Script] Generated: {script_path}")
    setup_messages.append(f"[CMD] {' '.join(cmd_parts)}")
    # Expose underlying bsub command (first non-comment line in runall.csh) for user clarity
    try:
        import itertools
        from pathlib import Path as _P
        script_lines = _P(script_path).read_text(errors='ignore').splitlines()
        bsub_line = next((ln for ln in script_lines if ln.strip().startswith('bsub ')), None)
        if bsub_line:
            setup_messages.append(f"[BSUB] {bsub_line}")
    except Exception:
        pass
    setup_messages.append(f"[WorkingDir] {quality_dir}")

    # Validate filesystem prerequisites early
    missing_paths: list[str] = []
    if not quality_dir.exists():
        missing_paths.append(f"Quality dir missing: {quality_dir}")
    cfg_parent = Path(configfile).parent
    if not cfg_parent.exists():
        missing_paths.append(f"Config parent missing: {cfg_parent}")
    if missing_paths:
        for m in missing_paths:
            setup_messages.append(f"[Preflight] {m}")

    executor = WebSocketStreamExecutor(websocket)

    try:
        await executor.execute_command(
            command=cmd_parts,
            working_dir=quality_dir,
            setup_messages=setup_messages,
        )
    except WebSocketDisconnect:
        # Client disconnected mid-run
        return
    except Exception as e:
        # Unexpected server-side error
        try:
            await websocket.send_json({"event": "error", "detail": f"Unexpected error: {e}"})
            await websocket.close()
        except Exception:
            pass

