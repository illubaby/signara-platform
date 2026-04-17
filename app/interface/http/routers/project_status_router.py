"""Project Status Router"""
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.application.cell.use_cases import (
    ListCells, 
    GetNetlistVersion, 
    GetNetlistVersionInput,
    GetCellPvtStatus,
    GetCellPvtStatusInput
)
from app.application.cell.report_status import (
    get_tmqa_reports_batch,
    get_tmqc_spice_vs_nt_reports_batch,
    get_tmqc_spice_vs_spice_reports_batch,
    get_equalization_reports_batch,
    check_special_check_exists,
    check_package_compare_exists,
    clear_report_caches
)
from app.application.cell.final_status import (
    get_final_status_cells_batch
)
from app.application.cell.pic_infor import GetPicInfor, GetPicInforInput
from app.infrastructure.p4.cell_repository_p4 import CellRepositoryP4
from app.infrastructure.p4.cell_repository_cached import CellRepositoryFileSystemCache
from app.application.project_status.use_cases import (
    BatchUpdateCellPic, BatchUpdateCellPicInput,
    BatchUpdateCellFields, BatchUpdateCellFieldsInput,
    RefreshJiraStatus, RefreshJiraStatusInput,
)
from app.infrastructure.processes.terminal_command_runner import SubprocessTerminalCommandRunner
import logging

router = APIRouter()
app_root = Path(__file__).resolve().parent.parent.parent.parent
templates = Jinja2Templates(directory=str(app_root / "presentation" / "templates"))


@router.get("/project-status", response_class=HTMLResponse)
def project_status_page(request: Request):
    """Render project status page"""
    return templates.TemplateResponse("project_status.html", {"request": request})


@router.get("/api/project-status/config")
def get_project_config(project: str, subproject: str):
    """Get project configuration (paths, etc)."""
    try:
        repo = CellRepositoryFileSystemCache(CellRepositoryP4())
        config = repo.get_project_config(project, subproject)
        
        # Add server working directory as absolute path
        import os
        config['server_cwd'] = os.getcwd()
        
        return {"config": config}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/project-status")
def get_project_status(
    project: str, 
    subproject: str, 
    refresh: bool = False,
    final_lib_path: str = Query(None, description="Custom path for final lib status check"),
    cutoff_date: str = Query(None, description="Cutoff date for report filtering (YYYY-MM-DD)")
):
    """Get project status data for specified project and subproject."""
    logger = logging.getLogger(__name__)
    logger.info("="*80)
    logger.info(f"[get_project_status] START - Project: {project}, Subproject: {subproject}, Refresh: {refresh}")
    logger.info("="*80)
    
    try:
        # Clear report status caches when refresh=True
        if refresh:
            logger.info(f"[get_project_status] Refresh=True - Clearing report caches for {project}/{subproject}")
            clear_report_caches(project, subproject)
        
        p4_repo = CellRepositoryP4()
        cached_repo = CellRepositoryFileSystemCache(p4_repo)
        
        logger.info(f"[get_project_status] Calling list_cells with refresh={refresh}")
        cells = cached_repo.list_cells(project, subproject, refresh=refresh)
        logger.info(f"[get_project_status] Received {len(cells)} cells from repository")
        
        use_case = ListCells(cells)
        result = use_case.execute()
        logger.info(f"[get_project_status] Use case executed, {len(result.cells)} cells")
        
        # Get project config to retrieve cutoff_date (if not provided as parameter)
        config = cached_repo.get_project_config(project, subproject)
        if not cutoff_date:
            cutoff_date = config.get('cutoff_date', None)
        logger.info(f"[get_project_status] Using cutoff_date: {cutoff_date}")
        
        # Populate tmqa and pvt_summary for each cell
        # Note: netlist_uc commented out (netlist_snaphier column disabled)
        # netlist_uc = GetNetlistVersion()
        pvt_uc = GetCellPvtStatus()
        
        # Query all report types once for all cells (batch optimization)
        # Pass cutoff_date to filter by file modification date
        try:
            tmqa_cells = get_tmqa_reports_batch(project, subproject, cutoff_date)
        except Exception:
            tmqa_cells = set()
        
        try:
            tmqc_spice_vs_nt_cells = get_tmqc_spice_vs_nt_reports_batch(project, subproject, cutoff_date)
            logger.info(f"[get_project_status] TMQC Spice vs NT reports found for {len(tmqc_spice_vs_nt_cells)} cells")
        except Exception as e:
            logger.error(f"[get_project_status] Error getting TMQC Spice vs NT reports: {e}")
            tmqc_spice_vs_nt_cells = set()
        
        try:
            tmqc_spice_vs_spice_cells = get_tmqc_spice_vs_spice_reports_batch(project, subproject, cutoff_date)
            logger.info(f"[get_project_status] TMQC Spice vs Spice reports found for {len(tmqc_spice_vs_spice_cells)} cells")
        except Exception as e:
            logger.error(f"[get_project_status] Error getting TMQC Spice vs Spice reports: {e}")
            tmqc_spice_vs_spice_cells = set()
        
        try:
            equalization_cells = get_equalization_reports_batch(project, subproject, cutoff_date)
            logger.info(f"[get_project_status] Equalization reports found for {len(equalization_cells)} cells")
        except Exception as e:
            logger.error(f"[get_project_status] Error getting Equalization reports: {e}")
            equalization_cells = set()
        
        try:
            final_status_cells = get_final_status_cells_batch(project, subproject, final_lib_path, cutoff_date)
            logger.info(f"[get_project_status] Final status found for {len(final_status_cells)} cells")
        except Exception as e:
            logger.error(f"[get_project_status] Error getting Final status: {e}")
            final_status_cells = set()
        
        # Check project-level reports
        try:
            special_check_exists = check_special_check_exists(project, subproject, cutoff_date)
        except Exception:
            special_check_exists = False
        
        try:
            package_compare_exists = check_package_compare_exists(project, subproject, cutoff_date)
        except Exception:
            package_compare_exists = False
        
        data = []
        for cell in result.cells:
            # Note: netlist_snaphier fetching commented out to speed up page load
            # Get netlist version
            # try:
            #     netlist_result = netlist_uc.execute(GetNetlistVersionInput(
            #         project=project,
            #         subproject=subproject,
            #         cell=cell.ckt_macros,
            #         cell_type=cell.tool.lower(),
            #         pic=cell.pic  # Use PIC's workspace if available
            #     ))
            #     cell.netlist_snaphier = netlist_result.netlist_version
            # except Exception:
            #     # If netlist version detection fails, leave it as None
            #     cell.netlist_snaphier = None
            
            # Check report statuses (using pre-fetched sets)
            cell.tmqa = "✓" if cell.ckt_macros in tmqa_cells else None
            # TMQC (Spice vs NT): preserve manual 'skip' overrides
            cached_tmqc = (cell.tmqc_spice_vs_nt or '').lower()
            if cached_tmqc == 'skip':
                cell.tmqc_spice_vs_nt = 'skip'
            else:
                if cell.tool and cell.tool.lower() == 'nt':
                    name_l = (cell.ckt_macros or '').lower()
                    if any(pat in name_l for pat in ('testout', 'tximp', 'vreg')):
                        cell.tmqc_spice_vs_nt = 'skip'
                    else:
                        cell.tmqc_spice_vs_nt = "✓" if cell.ckt_macros in tmqc_spice_vs_nt_cells else None
                else:
                    cell.tmqc_spice_vs_nt = "✓" if cell.ckt_macros in tmqc_spice_vs_nt_cells else None
            # TMQC (Spice vs Spice): preserve manual 'skip' overrides
            cached_spice_vs_spice = (cell.tmqc_spice_vs_spice or '').lower()
            if cached_spice_vs_spice == 'skip':
                cell.tmqc_spice_vs_spice = 'skip'
            else:
                cell.tmqc_spice_vs_spice = "✓" if cell.ckt_macros in tmqc_spice_vs_spice_cells else None

            # Equalization: preserve manual 'skip' overrides
            cached_equalization = (cell.equalization or '').lower()
            if cached_equalization == 'skip':
                cell.equalization = 'skip'
            else:
                cell.equalization = "✓" if cell.ckt_macros in equalization_cells else None
            
            # Check final status (raw_lib folder exists)
            cell.final_status = "✓" if cell.ckt_macros in final_status_cells else None
            
            # Get PVT status summary (only if PIC is assigned)
            if cell.pic:  # Only check PVT status if PIC is assigned
                try:
                    pvt_result = pvt_uc.execute(GetCellPvtStatusInput(
                        project=project,
                        subproject=subproject,
                        cell=cell.ckt_macros,
                        cell_type=cell.tool.lower(),  # tool is the cell_type
                        pic=cell.pic  # pic is the username
                    ))
                    cell.pvt_summary = pvt_result.summary
                except Exception:
                    # If PVT status detection fails, leave as None
                    pass
            
            data.append(cell.to_dict())
        
        # Get column metadata from entity definition
        from app.domain.cell.entities import Cell
        columns = Cell.get_column_metadata()
        
        return {
            "data": data, 
            "columns": columns,
            "project_status": {
                "special_check": "✓" if special_check_exists else None,
                "package_compare": "✓" if package_compare_exists else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/project-status/cells/{cell}/pvt-status")
def get_cell_pvt_status(
    cell: str,
    project: str = Query(...),
    subproject: str = Query(...),
    cell_type: str = Query(..., description="Cell type: 'sis' or 'nt'"),
    pic: str = Query(None, description="PIC username")
):
    """Get detailed PVT status for a specific cell."""
    try:
        pvt_uc = GetCellPvtStatus()
        result = pvt_uc.execute(GetCellPvtStatusInput(
            project=project,
            subproject=subproject,
            cell=cell,
            cell_type=cell_type,
            pic=pic
        ))
        
        return {
            "cell": result.cell,
            "cell_type": result.cell_type,
            "statuses": result.statuses,
            "summary": result.summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/project-status/update-pic")
async def update_pic(request: Request):
    """Batch update PIC values for cells and project config. Body: {project, subproject, updates: [{cell, pic}], config: {final_lib_path: ...}, hidden: [cell_names]}"""
    try:
        payload = await request.json()
        project = payload.get("project")
        subproject = payload.get("subproject")
        updates_raw = payload.get("updates", [])
        cell_updates_raw = payload.get("cell_updates", [])
        deletions_raw = payload.get("deletions", [])
        hidden_raw = payload.get("hidden", [])
        config_updates = payload.get("config", {})
        
        logger = logging.getLogger(__name__)
        logger.info(f"[update-pic] Received - project={project}, subproject={subproject}")
        logger.info(f"[update-pic] Updates: {len(updates_raw)} PICs, {len(cell_updates_raw)} fields, {len(deletions_raw)} deletions, {len(hidden_raw)} hidden")
        if hidden_raw:
            logger.info(f"[update-pic] Hidden cells to process: {hidden_raw}")
        
        updates = []
        for item in updates_raw:
            cell = item.get("cell")
            pic = item.get("pic") or None
            if cell:
                updates.append((cell, pic))
        
        repo = CellRepositoryFileSystemCache(CellRepositoryP4())
        
        # Update PIC values
        updated_count = 0
        if updates:
            use_case = BatchUpdateCellPic(repo)
            updated_count = use_case.execute(BatchUpdateCellPicInput(project=project, subproject=subproject, updates=updates))

        # Update arbitrary cell fields
        fields_updated = 0
        if cell_updates_raw:
            parsed = []
            for item in cell_updates_raw:
                cell = item.get('cell')
                values = item.get('values') or {}
                if cell and isinstance(values, dict) and values:
                    # PIC is persisted via the dedicated PIC batch path; avoid double-updates/uploads.
                    values = {k: v for (k, v) in values.items() if k != 'pic'}
                    if not values:
                        continue
                    parsed.append((cell, values))
            if parsed:
                fields_uc = BatchUpdateCellFields(repo)
                fields_updated = fields_uc.execute(BatchUpdateCellFieldsInput(project=project, subproject=subproject, updates=parsed))
        
        # Update project configuration (if provided)
        config_updated = False
        if config_updates:
            config_updated = repo.update_project_config(project, subproject, config_updates)

        # Process deletions (if any) - prefer batch method when available to submit once
        deletions_processed = 0
        deletions_failed = []
        if deletions_raw:
            # If repository has batch_delete_cells, use it for a single P4 submit
            if hasattr(repo, 'batch_delete_cells'):
                try:
                    deleted_count = repo.batch_delete_cells(project, subproject, deletions_raw)
                    deletions_processed = int(deleted_count or 0)
                    # If not all requested deletions processed, attempt individual deletes for remaining
                    if deletions_processed < len(deletions_raw):
                        # We won't try per-cell cleanup here to avoid double submits; list remaining as failed
                        deletions_failed = deletions_raw
                except Exception as ex:
                    logger = logging.getLogger(__name__)
                    logger.error(f"[batch_delete_cells] Batch delete failed: {ex}")
                    deletions_failed = deletions_raw
            else:
                # Fallback: individual deletes (will submit per-delete)
                for dcell in deletions_raw:
                    try:
                        success = repo.delete_cell(project, subproject, dcell)
                        if success:
                            deletions_processed += 1
                        else:
                            deletions_failed.append(dcell)
                    except Exception:
                        deletions_failed.append(dcell)
        
        # Process hidden cells (mark as hidden=true in JSON)
        hidden_processed = 0
        hidden_failed = []
        if hidden_raw:
            logger.info(f"[update-pic] Processing {len(hidden_raw)} hidden cells...")
            # Use batch update to set hidden flag for all cells at once
            hidden_updates = [(hcell, {'hidden': True}) for hcell in hidden_raw]
            try:
                fields_uc = BatchUpdateCellFields(repo)
                hidden_processed = fields_uc.execute(BatchUpdateCellFieldsInput(
                    project=project, 
                    subproject=subproject, 
                    updates=hidden_updates
                ))
                logger.info(f"[update-pic] Hidden cells processed: {hidden_processed}/{len(hidden_raw)}")
                # Any cells not processed are considered failed
                if hidden_processed < len(hidden_raw):
                    hidden_failed = hidden_raw[hidden_processed:]
                    logger.warning(f"[update-pic] Some cells failed to hide: {hidden_failed}")
            except Exception as ex:
                logger.error(f"[hide_cells] Batch hide failed: {ex}")
                hidden_failed = hidden_raw
        
        return {
            "updated": updated_count,
            "fields_updated": fields_updated,
            "config_updated": config_updated,
            "deletions_processed": deletions_processed,
            "deletions_failed": deletions_failed,
            "hidden_processed": hidden_processed,
            "hidden_failed": hidden_failed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/project-status/refresh-jira")
async def refresh_jira(request: Request):
    """Run JIRA status script for each cell's jira_link and update assignee/duedate/status.

    Body: { project, subproject }
    """
    try:
        # Temporarily disabled (frontend also stops calling this endpoint).
        raise HTTPException(status_code=503, detail="JIRA refresh temporarily disabled")

        payload = await request.json()
        project = payload.get("project")
        subproject = payload.get("subproject")
        if not project or not subproject:
            raise HTTPException(status_code=400, detail="project and subproject are required")

        logger = logging.getLogger(__name__)
        logger.info(f"[/refresh-jira] Request: project={project}, subproject={subproject}")
        p4_repo = CellRepositoryP4()
        repo = CellRepositoryFileSystemCache(p4_repo)
        runner = SubprocessTerminalCommandRunner()

        # Use app root as working directory to resolve relative script path
        app_root_str = str(app_root)
        uc = RefreshJiraStatus(repo, runner)
        updated = uc.execute(RefreshJiraStatusInput(project=project, subproject=subproject, workdir=app_root_str))
        logger.info(f"[/refresh-jira] fields_updated={updated}")

        return {"fields_updated": updated}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/project-status/delete-cell")
async def delete_cell(request: Request):
    """Delete a cell from the project. Body: {project, subproject, cell}"""
    try:
        payload = await request.json()
        project = payload.get("project")
        subproject = payload.get("subproject")
        cell = payload.get("cell")
        
        if not project or not subproject or not cell:
            raise HTTPException(status_code=400, detail="project, subproject, and cell are required")
        
        repo = CellRepositoryFileSystemCache(CellRepositoryP4())
        success = repo.delete_cell(project, subproject, cell)
        
        if success:
            return {"success": True, "message": f"Cell {cell} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Cell {cell} not found or could not be deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/project-status/add-cell")
async def add_cell(request: Request):
    """Add a new cell to the project. Body: {project, subproject, cell_data}"""
    try:
        payload = await request.json()
        project = payload.get("project")
        subproject = payload.get("subproject")
        cell_data = payload.get("cell_data")
        
        if not project or not subproject or not cell_data:
            raise HTTPException(status_code=400, detail="project, subproject, and cell_data are required")
        
        if not isinstance(cell_data, dict) or not cell_data.get("ckt_macros"):
            raise HTTPException(status_code=400, detail="cell_data must be a dict with at least ckt_macros field")
        
        repo = CellRepositoryFileSystemCache(CellRepositoryP4())
        success = repo.add_cell(project, subproject, cell_data)
        
        if success:
            return {"success": True, "message": f"Cell {cell_data.get('ckt_macros')} added successfully"}
        else:
            raise HTTPException(status_code=409, detail=f"Cell {cell_data.get('ckt_macros')} already exists or could not be added")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/project-status/get-pic")
async def get_pic(request: Request):
    """Suggest PIC values (type=SAF) for cells with empty PIC.

    Body: { project, subproject }
    """
    try:
        payload = await request.json()
        project = payload.get("project")
        subproject = payload.get("subproject")
        if not project or not subproject:
            raise HTTPException(status_code=400, detail="project and subproject are required")

        repo = CellRepositoryFileSystemCache(CellRepositoryP4())
        cells = repo.list_cells(project, subproject, refresh=False)

        uc = GetPicInfor()
        updates: list[tuple[str, str]] = []
        attempted: list[str] = []
        not_found: list[str] = []
        seen = set()

        for cell in cells:
            macro = getattr(cell, "ckt_macros", None)
            if not isinstance(macro, str) or not macro:
                continue
            if macro in seen:
                continue
            seen.add(macro)

            attempted.append(macro)
            result = uc.execute(GetPicInforInput(
                log_type="SAF",
                macro=macro,
                projectname=project,
                release=subproject,
            ))
            if result and result.username.strip():
                updates.append((macro, result.username.strip()))
            else:
                not_found.append(macro)

        return {
            "attempted": len(attempted),
            "found": len(updates),
            "not_found": not_found,
            "updates": [{"cell": c, "pic": p} for (c, p) in updates],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
