"""Use case for generating QC tables from CSV files and managing cache."""
from typing import Dict, List, Any, Optional
from pathlib import Path
from app.domain.qc.entities import TableRowData
from app.infrastructure.qc.testbench_repository_fs import TestbenchRepositoryFS
from app.infrastructure.qc.tables_repository_fs import TablesRepositoryFS
from app.infrastructure.qc.script_builder import RunAllScriptBuilder
from app.infrastructure.fs.timing_paths import TimingPaths


class GenerateQCTableUseCase:
    """Generate QC delay/constraint tables with caching and script generation."""
    
    def __init__(self, tb_repo: TestbenchRepositoryFS, cache: Dict[str, Dict[str, Any]]):
        """
        Args:
            tb_repo: Repository for testbench operations
            cache: Global cache dictionary for table data
        """
        self.tb_repo = tb_repo
        self.cache = cache
    
    def _cache_key(self, project: str, subproject: str, cell: str) -> str:
        """Generate cache key for cell."""
        return f"{project}::{subproject}::{cell}"
    
    def _get_cached_table(self, project: str, subproject: str, cell: str) -> Optional[dict]:
        """Get cached table data if available."""
        key = self._cache_key(project, subproject, cell)
        return self.cache.get(key)
    
    def _set_cached_table(self, project: str, subproject: str, cell: str, value: dict):
        """Store table data in cache."""
        key = self._cache_key(project, subproject, cell)
        self.cache[key] = value
    
    def execute(
        self,
        project: str,
        subproject: str,
        cell: str,
        qcplan: Optional[str],
        netlist: Optional[str],
        data: Optional[str],
        datastore: Optional[List[str]],
        common_source: Optional[str],
        timing_paths: Optional[str],
        ref_data: Optional[str],
        update: bool,
        adjustment: bool,
        no_wf: bool,
        xtalk_rel_net: bool,
        hierarchy: Optional[str],
        verbose: Optional[str],
        include: Optional[str],
        xtalk: Optional[str],
        primesim: Optional[str],
        hspice: Optional[str],
        include_file: Optional[str],
        primesim_version: Optional[str],
        hspice_version: Optional[str],
        index: Optional[str],
        phase: Optional[str],
        debug_path: Optional[str],
    ) -> dict:
        """
        Generate QC tables from CSV files or return cached data.
        
        Returns:
            dict with project, subproject, cell, delay, constraint, source, 
            applied_filters, cached, note, script_path, ran_script, testbenches
        """
        # Resolve cell root directory
        tp = TimingPaths(project, subproject)
        cell_root = tp.qc_cell_root(cell)
        
        # Create cell directory if it doesn't exist (for P4V-discovered cells)
        if not cell_root.exists():
            cell_root.mkdir(parents=True, exist_ok=True)
        
        # Create empty debug folder if debug_path not provided
        if not debug_path:
            empty_dir = cell_root / "empty"
            empty_dir.mkdir(parents=True, exist_ok=True)
            debug_path = str(empty_dir)
        
        # Check cache first
        cached_payload = self._get_cached_table(project, subproject, cell)
        
        if cached_payload:
            # Use cached data
            delay_rows = cached_payload.get("delay", [])
            constraint_rows = cached_payload.get("constraint", [])
            
            # Merge simulation testbenches
            sim_tbs = self.tb_repo.list_testbenches(project, subproject, cell)
            existing_tb = {r["testbench"] for r in delay_rows}
            
            for tb in sim_tbs:
                if tb not in existing_tb:
                    delay_rows.append({
                        "testbench": tb,
                        "pvt": "",
                        "status": "Pending",
                        "slack": None,
                        "factorx": None,
                        "program_time": None,
                        "path": None,
                        "log_file": None,
                        "notes": None
                    })
            
            # Always regenerate runall script
            script_path = cell_root / "runall.csh"
            content = self._build_runall_script(
                cell, project, subproject,
                qcplan, netlist, common_source, data, datastore, ref_data,
                update, adjustment, no_wf, xtalk_rel_net,
                hierarchy, verbose, include or include_file,
                xtalk, primesim or primesim_version,
                hspice or hspice_version, index, phase, debug_path
            )
            script_path.write_text(content)
            try:
                script_path.chmod(0o755)
            except Exception:
                pass
            
            return {
                "project": project,
                "subproject": subproject,
                "cell": cell,
                "delay": delay_rows,
                "constraint": constraint_rows,
                "source": cached_payload.get("source", {}),
                "applied_filters": cached_payload.get("applied_filters", {}),
                "cached": True,
                "note": "from cache",
                "script_path": str(script_path),
                "ran_script": False,
                "testbenches": sim_tbs,
            }
        
        # Build tables from CSV files
        tables_repo = TablesRepositoryFS()
        service_results = tables_repo.build_tables(timing_paths, data)
        
        delay_rows = [
            {
                "testbench": r.testbench,
                "pvt": r.pvt,
                "status": r.status,
                "slack": r.slack,
                "factorx": r.factorx,
                "program_time": r.program_time,
                "path": r.path,
                "log_file": None,
                "notes": None
            }
            for r in service_results["delay"]
        ]
        
        constraint_rows = [
            {
                "testbench": r.testbench,
                "pvt": r.pvt,
                "status": r.status,
                "slack": r.slack,
                "factorx": r.factorx,
                "program_time": r.program_time,
                "path": r.path,
                "log_file": None,
                "notes": None
            }
            for r in service_results["constraint"]
        ]
        
        # Cache the results
        payload = {
            "delay": delay_rows,
            "constraint": constraint_rows,
            "source": {
                "qcplan": qcplan,
                "netlist": netlist,
                "data": data,
                "common_source": common_source,
                "timing_paths": timing_paths,
                "ref_data": ref_data,
            },
            "applied_filters": {
                "update": update,
                "adjustment": adjustment,
                "no_wf": no_wf,
                "xtalk_rel_net": xtalk_rel_net,
                "xtalk": xtalk,
                "hierarchy": hierarchy,
                "verbose": verbose,
                "include": include or include_file,
                "primesim": primesim or primesim_version,
                "hspice": hspice or hspice_version,
                "index": index,
                "phase": phase,
            },
        }
        self._set_cached_table(project, subproject, cell, payload)
        
        # Merge simulation testbenches
        sim_tbs = self.tb_repo.list_testbenches(project, subproject, cell)
        existing_tb = {r["testbench"] for r in delay_rows}
        
        for tb in sim_tbs:
            if tb not in existing_tb:
                delay_rows.append({
                    "testbench": tb,
                    "pvt": "",
                    "status": "Pending",
                    "slack": None,
                    "factorx": None,
                    "program_time": None,
                    "path": None,
                    "log_file": None,
                    "notes": None
                })
        
        # Always generate runall script
        script_path = cell_root / "runall.csh"
        content = self._build_runall_script(
            cell, project, subproject,
            qcplan, netlist, common_source, data, datastore, ref_data,
            update, adjustment, no_wf, xtalk_rel_net,
            hierarchy, verbose, include or include_file,
            xtalk, primesim or primesim_version,
            hspice or hspice_version, index, phase, debug_path
        )
        script_path.write_text(content)
        try:
            script_path.chmod(0o755)
        except Exception:
            pass
        
        return {
            "project": project,
            "subproject": subproject,
            "cell": cell,
            "delay": delay_rows,
            "constraint": constraint_rows,
            "source": payload["source"],
            "applied_filters": payload["applied_filters"],
            "cached": False,
            "note": f"generated {len(delay_rows)} delay rows / {len(constraint_rows)} constraint rows",
            "script_path": str(script_path),
            "ran_script": False,
            "testbenches": sim_tbs,
        }
    
    def _build_runall_script(
        self,
        cell: str,
        project: str,
        subproject: str,
        qcplan: Optional[str],
        netlist: Optional[str],
        common_source: Optional[str],
        data: Optional[str],
        datastore: Optional[List[str]],
        ref_data: Optional[str],
        update: bool,
        adjustment: bool,
    no_wf: bool,
        xtalk_rel_net: bool,
        hierarchy: Optional[str],
        verbose: Optional[str],
        include: Optional[str],
        xtalk: Optional[str],
        primesim: Optional[str],
        hspice: Optional[str],
        index: Optional[str],
        phase: Optional[str],
        debug_path: Optional[str],
    ) -> str:
        """Build runall.csh script content - delegates to infrastructure."""
        # Convert to dict for infrastructure call
        req_params = {
            'qcplan': qcplan,
            'netlist': netlist,
            'data': data,
            'datastore': datastore,
            'common_source': common_source,
            'ref_data': ref_data,
            'update': update,
            'adjustment': adjustment,
            'no_wf': no_wf,
            'xtalk_rel_net': xtalk_rel_net,
            'hierarchy': hierarchy,
            'verbose': verbose,
            'include': include,
            'xtalk': xtalk,
            'primesim': primesim,
            'hspice': hspice,
            'index': index,
            'phase': phase,
            'debug_path': debug_path,
        }
        builder = RunAllScriptBuilder()
        return builder.build(cell, project, subproject, req_params)
