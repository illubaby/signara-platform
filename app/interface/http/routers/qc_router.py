"""QC Router - Architecture-compliant endpoints for Timing QC feature.

This router follows Clean Architecture principles:
- Thin HTTP layer - no business logic
- Uses dependency injection for use cases
- Maps domain entities to Pydantic schemas
- Delegates all logic to application use cases

Prefix: /api/qc (not /api/timing-qc - that's the legacy router)
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends, WebSocket
from fastapi.websockets import WebSocketDisconnect
from typing import Optional, List, Dict
from pathlib import Path
import os
import asyncio
import subprocess
import shutil
import shlex
import re
import getpass

# Import reusable WebSocket streaming infrastructure
from app.infrastructure.websocket.stream_executor import WebSocketStreamExecutor

# Phase 1, 2, 3: Import schemas from new qc.py
from app.interface.http.schemas.qc import (
    QCCell, QCCellList, QCDefaults, TestbenchList, ImportantArcs,
    TestbenchStatus, PVTRow, GenerateRequest, GenerateResult, TableRow,
    QCFileList, QCFileRead, QCFileWriteRequest, QCFileWriteResponse,
    LogResult, RunScriptResult, RunPvtsRequest, RunPvtsResult,
    PvtJobResult, RunRowRequest, RunRowResult,
    EqualizerRow, EqualizerData, EqualizerUpdateRequest
)
from app.interface.dependencies.explorer_dep import (
    get_list_directory_use_case,
    get_read_file_use_case,
    get_write_file_use_case,
)
from app.interface.dependencies.qc_dep import (
    get_create_task_queue_use_case,
    get_get_task_queue_use_case,
    get_list_cells_use_case,
    get_defaults_use_case,
    get_list_testbenches_use_case,
    get_important_arcs_use_case,
    get_testbench_status_use_case,
    get_generate_qc_table_use_case,
)
from app.application.explorer.use_cases import (
    ListDirectoryInput, ReadFileInput, WriteFileInput
)
from app.domain.explorer.errors import PathViolation as ExplorerPathViolation
from app.interface.http.schemas.task_queue import (
    TaskQueueRequestSchema as TaskQueueRequest,
    TaskQueueResultSchema as TaskQueueResult,
    TaskQueueStatusSchema as TaskQueueStatus
)
from app.domain.common.validation import validate_component, ValidationError
from app.infrastructure.fs.symlink_service import SymlinkService
from app.interface.dependencies.impostor_dep import (
    get_run_bsub_with_impostor_uc,
    get_impostor_mapping_uc
)
from app.infrastructure.fs.project_root import PROJECTS_BASE as BASE_DIR
from app.infrastructure.fs.timing_paths import TimingPaths

router = APIRouter(prefix="/api/qc", tags=["qc"])


# ============================================================================
# Helper functions (temporary - will be moved to use cases in later phases)
# ============================================================================

def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

def _resolve_testbench_root(project: str, subproject: str, cell: str, testbench: str) -> Path:
    """Resolve testbench root directory (canonical or legacy)."""
    tp = TimingPaths(project, subproject)
    return tp.qc_testbench_root(cell, testbench)


# ============================================================================
# Cell Listing Endpoints (Phase 1)
# ============================================================================

@router.get("/{project}/{subproject}/cells", response_model=QCCellList)
async def list_qc_cells(
    project: str,
    subproject: str,
    uc = Depends(get_list_cells_use_case)
):
    """List all QC cells (local filesystem + P4V) with metadata.
    
    Returns cells sorted by name (reverse) with flags indicating presence of:
    - QcPlan file
    - Netlist
    - Data directory
    - Common source
    - Reference data
    - Row counts (from cache if available)
    """
    for v, f in ((project, "project"), (subproject, "subproject")):
        _validate_component(v, f)
    
    cells_meta = uc.execute(project, subproject)
    
    # Convert domain entities to response models
    cells = []
    for c in cells_meta:
        # Check if TMQC report exists
        tmqc_report_exists = None
        try:
            report_path = BASE_DIR / project / subproject / 'design' / 'timing' / 'quality' / '4_qc' / c.cell / f"{c.cell}_TMQC_Report.xlsx"
            tmqc_report_exists = report_path.exists()
        except Exception:
            tmqc_report_exists = None
        
        cells.append(QCCell(
            cell=c.cell,
            has_qcplan=c.has_qcplan,
            has_netlist=c.has_netlist,
            has_data=c.has_data,
            has_common_source=c.has_common_source,
            has_ref=c.has_ref,
            delay_rows=c.delay_rows,
            constraint_rows=c.constraint_rows,
            tmqc_report_exists=tmqc_report_exists,
        ))
    
    note = None if cells else "No cell directories under quality/4_qc/"
    return QCCellList(project=project, subproject=subproject, cells=cells, note=note)


# ============================================================================
# Defaults Endpoints (Phase 2)
# ============================================================================

@router.get("/{project}/{subproject}/defaults", response_model=QCDefaults)
async def qc_defaults(
    project: str,
    subproject: str,
    cell: str = Query(..., description="Cell name"),
    force_defaults: bool = Query(False, description="If true, ignore existing runall.csh and return fresh defaults"),
    uc = Depends(get_defaults_use_case)
):
    """Get default QC paths and options for a cell.
    
    Returns default paths for:
    - QcPlan file (P4V depot path)
    - Netlist
    - Data directory (raw_lib)
    - Common source
    - Timing paths CSV
    - Reference data
    
    If runall.csh exists in cell directory and force_defaults=False,
    parses script to extract existing configuration.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    defaults = uc.execute(project, subproject, cell, force_defaults)
    
    # Convert domain entity to response model
    return QCDefaults(
        project=project,
        subproject=subproject,
        cell=cell,
        qcplan_path=defaults.qcplan_path,
        netlist_path=defaults.netlist_path,
        data_path=defaults.data_path,
        datastore_paths=defaults.datastore_paths,
        common_source_path=defaults.common_source_path,
        timing_paths_path=defaults.timing_paths_path,
        ref_data_path=defaults.ref_data_path,
        update=defaults.update,
        adjustment=defaults.adjustment,
    no_wf=defaults.no_wf,
        xtalk_rel_net=defaults.xtalk_rel_net,
        hierarchy=defaults.hierarchy,
        verbose=defaults.verbose,
        include=defaults.include,
        xtalk=defaults.xtalk,
        primesim=defaults.primesim,
        hspice=defaults.hspice,
        index=defaults.index,
        phase=defaults.phase,
        debug_path=defaults.debug_path,
        tmqc_internal_node_map_path=defaults.tmqc_internal_node_map_path,
        note=defaults.note,
    )


# ============================================================================
# Testbench Endpoints (Phase 3)
# ============================================================================

@router.get("/{project}/{subproject}/testbenches", response_model=TestbenchList)
async def list_testbenches(
    project: str,
    subproject: str,
    cell: str = Query(..., description="Cell name"),
    uc = Depends(get_list_testbenches_use_case)
):
    """List all testbenches for a QC cell.
    
    Scans for testbench directories under:
    - simulations_{cell}/ (canonical)
    - simulation_{cell}/ (legacy fallback)
    
    Returns directory names only (not full paths).
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    tbs = uc.execute(project, subproject, cell)
    note = None if tbs else "No testbench directories found (look for simulations_<cell>/)"
    return TestbenchList(project=project, subproject=subproject, cell=cell, testbenches=tbs, note=note)


@router.get("/{project}/{subproject}/important-arcs", response_model=ImportantArcs)
async def get_important_arcs(
    project: str,
    subproject: str,
    cell: str = Query(..., description="Cell name"),
    uc = Depends(get_important_arcs_use_case)
):
    """Get testbench numbers marked as important from important_arc.csv.
    
    Looks for important_arc.csv in the cell directory and extracts testbench numbers.
    The CSV should have testbench numbers (one per row or in columns).
    Used by UI to highlight important testbenches.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    important_numbers = uc.execute(project, subproject, cell)
    
    note = None
    if important_numbers:
        note = f"Found {len(important_numbers)} important testbench numbers"
    else:
        note = "important_arc.csv not found or empty"
    
    return ImportantArcs(
        project=project,
        subproject=subproject,
        cell=cell,
        important_numbers=important_numbers,
        note=note
    )


@router.get("/{project}/{subproject}/status", response_model=TestbenchStatus)
async def get_testbench_status(
    project: str,
    subproject: str,
    cell: str = Query(..., description="Cell name"),
    testbench: str = Query(..., description="Testbench directory name"),
    uc = Depends(get_testbench_status_use_case)
):
    """Get execution status for a testbench with PVT breakdown.
    
    Returns status for each PVT configuration found in the testbench directory,
    along with an aggregated overall status (Passed/Fail/In Progress/Not Started).
    
    Directory layout expected:
      quality/4_qc/<cell>/simulations_<cell>/<testbench>/<pvt>/siliconsmart.log
    or  quality/4_qc/<cell>/simulations_<cell>/<testbench>/<pvt>/primelib.log
    (legacy simulation_<cell>/ also supported).
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    try:
        result = uc.execute(project, subproject, cell, testbench)
        
        # Convert PVTRowMeta domain entities to PVTRow schemas
        pvt_rows = [
            PVTRow(
                pvt=p.pvt,
                status=p.status,
                log_type=p.log_type,
                log_path=p.log_path,
                pocv_file_status=p.pocv_file_status,
                note=p.note
            )
            for p in result["pvts"]
        ]
        
        return TestbenchStatus(
            project=result["project"],
            subproject=result["subproject"],
            cell=result["cell"],
            testbench=result["testbench"],
            pvts=pvt_rows,
            status=result["status"],
            note=result.get("note")
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get testbench status: {e}")


@router.post("/{project}/{subproject}/generate", response_model=GenerateResult)
async def generate_qc_table(
    project: str,
    subproject: str,
    req: GenerateRequest = Body(...),
    uc = Depends(get_generate_qc_table_use_case)
):
    """Generate QC delay/constraint tables from CSV files with caching.
    
    This endpoint:
    1. Checks cache for existing table data
    2. If not cached, builds tables from CSV files (timing_paths, data)
    3. Merges with simulation testbenches discovered in filesystem
    4. Generates runall.csh script for execution
    5. Caches results for subsequent calls
    
    Returns both delay and constraint tables with testbench/PVT combinations.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (req.cell, "cell")):
        _validate_component(v, f)
    
    try:
        result = uc.execute(
            project=project,
            subproject=subproject,
            cell=req.cell,
            qcplan=req.qcplan,
            netlist=req.netlist,
            data=req.data,
            datastore=req.datastore,
            common_source=req.common_source,
            timing_paths=req.timing_paths,
            ref_data=req.ref_data,
            update=req.update,
            adjustment=req.adjustment,
            no_wf=req.no_wf,
            xtalk_rel_net=req.xtalk_rel_net,
            hierarchy=req.hierarchy,
            verbose=req.verbose,
            include=req.include,
            xtalk=req.xtalk,
            primesim=req.primesim,
            hspice=req.hspice,
            include_file=req.include_file,
            primesim_version=req.primesim_version,
            hspice_version=req.hspice_version,
            index=req.index,
            phase=req.phase,
            debug_path=req.debug_path,
        )
        
        # Convert dict rows to TableRow schemas
        delay_rows = [TableRow(**r) for r in result["delay"]]
        constraint_rows = [TableRow(**r) for r in result["constraint"]]
        
        return GenerateResult(
            project=result["project"],
            subproject=result["subproject"],
            cell=result["cell"],
            delay=delay_rows,
            constraint=constraint_rows,
            source=result["source"],
            applied_filters=result["applied_filters"],
            cached=result["cached"],
            note=result.get("note"),
            script_path=result.get("script_path"),
            ran_script=result["ran_script"],
            testbenches=result["testbenches"],
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate QC table: {e}")


# ============================================================================
# Explorer Endpoints (Phase 6.2)
# ============================================================================

@router.get("/{project}/{subproject}/explorer/list", response_model=QCFileList)
async def list_files(
    project: str,
    subproject: str,
    cell: str = Query(...),
    testbench: str = Query(...),
    pvt: Optional[str] = Query(None, description="Optional PVT folder under testbench to scope root"),
    path: str = Query('', description="Relative path under selected root (pvt or testbench). Empty for root."),
):
    """List files in QC testbench or PVT directory.
    
    Path hierarchy:
    - Without pvt: quality/4_qc/{cell}/simulations_{cell}/{testbench}/
    - With pvt: quality/4_qc/{cell}/simulations_{cell}/{testbench}/{pvt}/
    
    Note: 'netlists' is NOT a valid PVT root.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    root = _resolve_testbench_root(project, subproject, cell, testbench)
    if not root.exists():
        raise HTTPException(status_code=404, detail="Testbench directory not found")
    
    if pvt:
        # 'netlists' is explicitly NOT a PVT browse root per requirement
        if pvt.lower() == 'netlists':
            raise HTTPException(status_code=400, detail="'netlists' is not a PVT root")
        root = root / pvt
    
    try:
        uc = get_list_directory_use_case(str(root))
        out = uc.execute(ListDirectoryInput(relative=path or '', allow_external=True))
        entries = [e.__dict__ for e in out.entries]
    except ExplorerPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"List error: {e}")
    
    return QCFileList(
        project=project, 
        subproject=subproject, 
        cell=cell, 
        testbench=testbench, 
        pvt=pvt, 
        path=path or '', 
        entries=entries
    )


@router.get("/{project}/{subproject}/explorer/read", response_model=QCFileRead)
async def read_file(
    project: str,
    subproject: str,
    cell: str = Query(...),
    testbench: str = Query(...),
    pvt: Optional[str] = Query(None),
    file: str = Query(..., description="Relative file path under chosen root"),
):
    """Read file content from QC testbench or PVT directory."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    root = _resolve_testbench_root(project, subproject, cell, testbench)
    if not root.exists():
        raise HTTPException(status_code=404, detail="Testbench directory not found")
    
    if pvt:
        if pvt.lower() == 'netlists':
            raise HTTPException(status_code=400, detail="'netlists' is not a PVT root")
        root = root / pvt
    
    try:
        uc = get_read_file_use_case(str(root))
        out = uc.execute(ReadFileInput(relative=file, allow_external=True))
        fc = out.content
    except ExplorerPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Read error: {e}")
    
    return QCFileRead(
        project=project,
        subproject=subproject,
        cell=cell,
        testbench=testbench,
        pvt=pvt,
        path=file,
        name=fc.name,
        size=fc.size,
        is_text=fc.is_text,
        truncated=fc.truncated,
        content=fc.content if fc.is_text else None,
    )


@router.put("/{project}/{subproject}/explorer/write", response_model=QCFileWriteResponse)
async def write_file(
    project: str,
    subproject: str,
    cell: str = Query(...),
    testbench: str = Query(...),
    pvt: Optional[str] = Query(None),
    req: QCFileWriteRequest = Body(...),
):
    """Write file content to QC testbench or PVT directory."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    root = _resolve_testbench_root(project, subproject, cell, testbench)
    if not root.exists():
        raise HTTPException(status_code=404, detail="Testbench directory not found")
    
    if pvt:
        if pvt.lower() == 'netlists':
            raise HTTPException(status_code=400, detail="'netlists' is not a PVT root")
        root = root / pvt
    
    try:
        uc = get_write_file_use_case(str(root))
        out = uc.execute(WriteFileInput(relative=req.path, content=req.content))
        result = out.result
    except ExplorerPathViolation as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Write error: {e}")
    
    return QCFileWriteResponse(
        project=project,
        subproject=subproject,
        cell=cell,
        testbench=testbench,
        pvt=pvt,
        name=result.name,
        bytes_written=result.bytes_written,
        created=result.created,
        note="written",
    )


# ============================================================================
# Task Queue Endpoints (Phase 6.3)
# ============================================================================

@router.post("/{project}/{subproject}/cells/{cell}/taskqueue", response_model=TaskQueueResult)
async def create_task_queue(
    project: str,
    subproject: str,
    cell: str,
    testbench: str = Query(..., description="Testbench name to create task queue files in"),
    req: TaskQueueRequest = Body(...),
    uc = Depends(get_create_task_queue_use_case)
):
    """Create or update sis_task_queue.tcl and optionally monte_carlo_settings.tcl for a QC testbench."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    # Resolve testbench directory
    tb_root = _resolve_testbench_root(project, subproject, cell, testbench)
    if not tb_root.exists():
        raise HTTPException(status_code=404, detail=f"Testbench directory not found: {tb_root}")
    
    try:
        result = uc.execute(tb_root, project, subproject, f"{cell}/{testbench}", req)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return result


@router.get("/{project}/{subproject}/cells/{cell}/taskqueue", response_model=TaskQueueStatus)
async def get_task_queue(
    project: str,
    subproject: str,
    cell: str,
    testbench: str = Query(..., description="Testbench name to read task queue files from"),
    uc = Depends(get_get_task_queue_use_case)
):
    """Retrieve existing task queue configuration for a QC testbench."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench")):
        _validate_component(v, f)
    
    # Resolve testbench directory
    tb_root = _resolve_testbench_root(project, subproject, cell, testbench)
    if not tb_root.exists():
        raise HTTPException(status_code=404, detail=f"Testbench directory not found: {tb_root}")
    
    return uc.execute(tb_root, project, subproject, f"{cell}/{testbench}")


# ============================================================================
# Log Endpoint (Phase 6.4)
# ============================================================================

@router.get("/{project}/{subproject}/log", response_model=LogResult)
async def fetch_log(
    project: str,
    subproject: str,
    cell: str = Query(...),
    testbench: str = Query(...),
    pvt: str = Query(...),
    mode: str = Query("delay"),
    max_bytes: int = Query(40000, ge=1000, le=500000),
):
    """Fetch log file with optional truncation.
    
    Returns the last max_bytes of the log file if it exceeds the limit.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (testbench, "testbench"), (pvt, "pvt")):
        _validate_component(v, f)
    
    tp = TimingPaths(project, subproject)
    cell_root = tp.qc_cell_root(cell)
    log_path = cell_root / "logs" / f"{testbench}_{pvt}_{mode}.log"
    exists = log_path.exists()
    content = None
    truncated = False
    
    if exists:
        try:
            data = log_path.read_bytes()
            if len(data) > max_bytes:
                content = data[-max_bytes:].decode(errors="ignore")
                truncated = True
            else:
                content = data.decode(errors="ignore")
        except Exception:
            content = None
    
    return LogResult(
        project=project,
        subproject=subproject,
        cell=cell,
        testbench=testbench,
        pvt=pvt,
        mode=mode,
        path=str(log_path) if exists else None,
        exists=exists,
        content=content,
        truncated=truncated,
    )


# ============================================================================
# Script Execution Endpoints (Phase 7)
# ============================================================================

@router.post("/{project}/{subproject}/run-script", response_model=RunScriptResult)
async def run_qc_script(project: str, subproject: str, cell: str = Body(..., embed=True)):
    """Execute runall.csh script synchronously (fire and forget)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
        _validate_component(v, f)
    
    tp = TimingPaths(project, subproject)
    cell_root = tp.qc_cell_root(cell)
    script_path = cell_root / "runall.csh"
    
    if not script_path.exists():
        raise HTTPException(status_code=404, detail="runall.csh not found. Generate first.")
    
    try:
        # Force unbuffered python for any downstream python invocations
        env = os.environ.copy()
        env.setdefault("PYTHONUNBUFFERED", "1")
        subprocess.Popen(["/bin/csh", script_path.name], cwd=str(cell_root), env=env)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="/bin/csh not found on host")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start script: {e}")
    
    return RunScriptResult(
        project=project,
        subproject=subproject,
        cell=cell,
        script_path=str(script_path),
        started=True,
        cmd=f"/bin/csh {script_path.name}",
        working_dir=str(cell_root),
        note="launched",
    )


@router.websocket("/{project}/{subproject}/run-script/ws")
async def run_qc_script_ws(websocket: WebSocket, project: str, subproject: str, cell: str):
    """Execute runall.csh with WebSocket streaming of output.
    
    Now uses reusable WebSocketStreamExecutor infrastructure component.
    """
    # Accept WebSocket connection early to send validation errors
    await websocket.accept()
    
    try:
        # Validate components
        for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell")):
            _validate_component(v, f)
        
        tp = TimingPaths(project, subproject)
        cell_root = tp.qc_cell_root(cell)
        
        # Prepare setup messages
        setup_messages = []
        
        # Create cell directory if it doesn't exist (for P4V-discovered cells)
        if not cell_root.exists():
            try:
                cell_root.mkdir(parents=True, exist_ok=True)
                setup_messages.append(f"[Setup] Created cell directory: {cell_root}\n")
            except Exception as e:
                await websocket.send_json({"event": "error", "detail": f"Failed to create cell directory: {e}"})
                await websocket.close()
                return
        
        script_path = cell_root / "runall.csh"
        if not script_path.exists():
            await websocket.send_json({"event": "error", "detail": "runall.csh not found. Generate first."})
            await websocket.close()
            return
        
        # Create raw_lib folder (Data path) if it doesn't exist
        try:
            default_data_path = BASE_DIR / project / subproject / "design" / "timing" / "release" / "internal" / "raw_lib"
            if not default_data_path.exists():
                default_data_path.mkdir(parents=True, exist_ok=True)
                setup_messages.append(f"[Setup] Created Data directory: {default_data_path}\n")
        except Exception as e:
            setup_messages.append(f"[Warning] Failed to create Data directory: {e}\n")
        
        # Create symbolic links before running the script
        try:
            symlink_svc = SymlinkService()
            symlink_result = symlink_svc.link_cell_tools(cell_root)
            if symlink_result.warnings:
                setup_messages.append(f"[Symlink Setup] {symlink_result.note}\n")
        except Exception as e:
            setup_messages.append(f"[Warning] Failed to create symlinks: {e}\n")
        
        # Use reusable WebSocketStreamExecutor
        # This handles all subprocess management, streaming, and cleanup
        executor = WebSocketStreamExecutor(websocket)
        result = await executor.execute_script(
            script_path=script_path,
            working_dir=cell_root,
            shell="/bin/csh",
            setup_messages=setup_messages
        )
        
        # Close WebSocket (executor already sent completion event)
        try:
            await websocket.close()
        except Exception:
            pass
            
    except Exception as e:
        # Any unexpected error - executor handles WebSocket cleanup
        try:
            await websocket.send_json({"event": "error", "detail": f"Unexpected error: {e}"})
            await websocket.close()
        except Exception:
            pass


@router.post("/{project}/{subproject}/cells/{cell}/run-pvts", response_model=RunPvtsResult)
async def run_qc_pvts(
    project: str,
    subproject: str,
    cell: str,
    req: RunPvtsRequest = Body(...)
):
    """Submit bsub jobs to run individual PVTs for a testbench.
    
    Supports impostor mode where jobs are submitted under different user credentials.
    """
    for v, f in ((project, "project"), (subproject, "subproject"), (cell, "cell"), (req.testbench, "testbench")):
        _validate_component(v, f)
    
    tb_root = _resolve_testbench_root(project, subproject, cell, req.testbench)
    if not tb_root.exists():
        raise HTTPException(status_code=404, detail=f"Testbench directory not found: {tb_root}")
    
    jobs: List[PvtJobResult] = []
    
    # Extract testbench name components for job naming
    tb_name = req.testbench
    job_prefix = "QC"
    
    # Try to extract meaningful part
    if tb_name.startswith("testbench_"):
        parts = tb_name[len("testbench_"):].split("_")
        if parts:
            job_prefix = f"QC_{parts[0]}"
    else:
        job_prefix = f"QC_{tb_name}"
    
    for pvt in req.pvts:
        _validate_component(pvt, "pvt")
        pvt_dir = tb_root / pvt
        runqc_script = pvt_dir / "runQC.csh"
        
        if not runqc_script.exists():
            jobs.append(PvtJobResult(
                pvt=pvt,
                success=False,
                message=f"runQC.csh not found in {pvt_dir}"
            ))
            continue
        
        # Build job name
        job_name = f"{job_prefix}_{pvt}"
        if req.impostor and req.impostor != "self":
            current_user = getpass.getuser()
            job_name = f"{job_name}_{current_user}_impostor"
        
        # Parse queue options
        try:
            queue_opts_list = shlex.split(req.queue_opts)
        except Exception:
            queue_opts_list = req.queue_opts.split()
        
        # Build bsub command
        cmd_parts = ["bsub"] + queue_opts_list + [
            "-o", "/dev/null",
            "-e", "/dev/null",
            "-J", job_name,
            str(runqc_script)
        ]
        
        cmd_str = " ".join(shlex.quote(str(p)) for p in cmd_parts)
        
        try:
            # Check if bsub is available
            if not shutil.which("bsub"):
                jobs.append(PvtJobResult(
                    pvt=pvt,
                    success=False,
                    message="bsub command not found on host",
                    command=cmd_str
                ))
                continue
            
            # Determine execution mode: impostor or self
            if req.impostor and req.impostor != "self":
                # Run via impostor mechanism
                try:
                    run_impostor_uc = get_run_bsub_with_impostor_uc()
                    impostor_mapping_uc = get_impostor_mapping_uc()
                    impostor_map = impostor_mapping_uc.execute()
                    
                    result = run_impostor_uc.execute(
                        impostor_key=req.impostor,
                        bsub_cmd=cmd_parts,
                        cwd=pvt_dir
                    )
                    
                    if result.success:
                        jobs.append(PvtJobResult(
                            pvt=pvt,
                            success=True,
                            job_id=result.job_id,
                            message=f"{result.message} (as {impostor_map.get(req.impostor, 'unknown')})",
                            command=result.full_command or cmd_str
                        ))
                    else:
                        jobs.append(PvtJobResult(
                            pvt=pvt,
                            success=False,
                            message=f"Impostor execution failed: {result.message}",
                            command=result.full_command or cmd_str
                        ))
                except Exception as e:
                    jobs.append(PvtJobResult(
                        pvt=pvt,
                        success=False,
                        message=f"Impostor error: {e}",
                        command=cmd_str
                    ))
            else:
                # Execute bsub directly (as current user)
                result = subprocess.run(
                    cmd_parts,
                    cwd=str(pvt_dir),
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    # Parse job ID from output
                    job_id = None
                    match = re.search(r'Job <(\d+)>', result.stdout)
                    if match:
                        job_id = match.group(1)
                    
                    jobs.append(PvtJobResult(
                        pvt=pvt,
                        success=True,
                        job_id=job_id,
                        message=result.stdout.strip() or "Submitted",
                        command=cmd_str
                    ))
                else:
                    jobs.append(PvtJobResult(
                        pvt=pvt,
                        success=False,
                        message=result.stderr.strip() or result.stdout.strip() or "bsub failed",
                        command=cmd_str
                    ))
        except subprocess.TimeoutExpired:
            jobs.append(PvtJobResult(
                pvt=pvt,
                success=False,
                message="bsub command timed out",
                command=cmd_str
            ))
        except Exception as e:
            jobs.append(PvtJobResult(
                pvt=pvt,
                success=False,
                message=str(e),
                command=cmd_str
            ))
    
    return RunPvtsResult(
        project=project,
        subproject=subproject,
        cell=cell,
        testbench=req.testbench,
        jobs=jobs,
        note=f"Submitted {sum(1 for j in jobs if j.success)}/{len(jobs)} jobs" + (f" (via {req.impostor})" if req.impostor else "")
    )


@router.post("/{project}/{subproject}/run-row", response_model=RunRowResult)
async def run_qc_row(project: str, subproject: str, req: RunRowRequest = Body(...)):
    """Row-level QC execution stub (integration TBD)."""
    for v, f in ((project, "project"), (subproject, "subproject"), (req.cell, "cell"), (req.testbench, "testbench"), (req.pvt, "pvt"), (req.mode, "mode")):
        _validate_component(v, f)
    
    tp = TimingPaths(project, subproject)
    cell_root = tp.qc_cell_root(req.cell)
    if not cell_root.exists():
        raise HTTPException(status_code=404, detail="Cell directory not found")
    
    cmd = f"TimingCloseBeta.py -qc -cell {req.cell} -tb {req.testbench} -pvt {req.pvt} -mode {req.mode}"
    
    return RunRowResult(
        project=project,
        subproject=subproject,
        cell=req.cell,
        testbench=req.testbench,
        pvt=req.pvt,
        mode=req.mode,
        started=True,
        cmd=cmd,
        working_dir=str(cell_root),
        note="dispatch stub (integration TBD)",
    )


# ============================================================================
# Equalizer Endpoints
# ============================================================================

@router.get("/{project}/{subproject}/equalizer", response_model=EqualizerData)
async def get_equalizer_data(
    project: str,
    subproject: str,
    cell: str = Query(...),
):
    """Read EqualizeMap.csv from cell's Equalizer directory."""
    import csv
    
    _validate_component(project, "project")
    _validate_component(subproject, "subproject")
    _validate_component(cell, "cell")
    
    tp = TimingPaths(project, subproject)
    equalizer_file = tp.qc_cell_root(cell) / "Equalizer" / "EqualizeMap.csv"
    
    if not equalizer_file.exists():
        return EqualizerData(
            project=project,
            subproject=subproject,
            cell=cell,
            rows=[],
            exists=False,
            note="EqualizeMap.csv not found"
        )
    
    rows = []
    try:
        with open(equalizer_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(EqualizerRow(
                    action=row.get('#Action', '').strip(),
                    type=row.get('Type', '').strip(),
                    pin=row.get('Pin', '').strip(),
                    related_pin=row.get('Related Pin', '').strip(),
                    when=row.get('When', '').strip(),
                    ff_max_min=row.get('FF-Max/Min', '').strip(),
                    tt_max_min=row.get('TT-Max/Min', '').strip(),
                    ss_max_min=row.get('SS-Max/Min', '').strip(),
                    sf_max_min=row.get('SF-Max/Min', '').strip(),
                    status=row.get('Status', '').strip(),
                    extra_margin=row.get('Extra Margin', 'NA').strip()
                ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading CSV: {e}")
    
    return EqualizerData(
        project=project,
        subproject=subproject,
        cell=cell,
        rows=rows,
        exists=True,
        note=f"Loaded {len(rows)} rows"
    )


@router.put("/{project}/{subproject}/equalizer", response_model=EqualizerData)
async def update_equalizer_data(
    project: str,
    subproject: str,
    cell: str = Query(...),
    req: EqualizerUpdateRequest = Body(...),
):
    """Write updated data to EqualizeMap.csv."""
    import csv
    
    _validate_component(project, "project")
    _validate_component(subproject, "subproject")
    _validate_component(cell, "cell")
    
    tp = TimingPaths(project, subproject)
    equalizer_dir = tp.qc_cell_root(cell) / "Equalizer"
    equalizer_file = equalizer_dir / "EqualizeMap.csv"
    
    # Create directory if it doesn't exist
    equalizer_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(equalizer_file, 'w', encoding='utf-8', newline='') as f:
            fieldnames = ['#Action', 'Type', 'Pin', 'Related Pin', 'When', 'FF-Max/Min', 
                         'TT-Max/Min', 'SS-Max/Min', 'SF-Max/Min', 'Status', 'Extra Margin']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in req.rows:
                writer.writerow({
                    '#Action': row.action,
                    'Type': row.type,
                    'Pin': row.pin,
                    'Related Pin': row.related_pin,
                    'When': row.when,
                    'FF-Max/Min': row.ff_max_min,
                    'TT-Max/Min': row.tt_max_min,
                    'SS-Max/Min': row.ss_max_min,
                    'SF-Max/Min': row.sf_max_min,
                    'Status': row.status,
                    'Extra Margin': row.extra_margin
                })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing CSV: {e}")
    
    return EqualizerData(
        project=project,
        subproject=subproject,
        cell=cell,
        rows=req.rows,
        exists=True,
        note=f"Saved {len(req.rows)} rows"
    )

