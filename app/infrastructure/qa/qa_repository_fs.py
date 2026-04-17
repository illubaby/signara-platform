"""Filesystem implementation of QA repository."""
from typing import List, Optional, Dict, Any
from pathlib import Path
import csv
import os
import uuid
import threading
import subprocess
import time

from app.domain.qa.entities import (
    QACell, QASummary, QASummaryRow, QADefaults, QARunRequest, QARunResult, QAJobStatus,
    BriefSumItem, CellCheckMatrix
)
from app.domain.qa.repositories import QARepository, DISPLAY_CHECKS, MANDATORY_CHECKS
from app.infrastructure.fs.timing_paths import TimingPaths
from app.infrastructure.fs.symlink_service import SymlinkService


class QARepositoryFS:
    """Filesystem-based implementation of QA repository."""
    
    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}
    
    def list_cells(self, project: str, subproject: str) -> List[QACell]:
        """List all QA cells from filesystem."""
        root = self._qa_root(project, subproject)
        if not root.exists():
            return []
        
        cells: List[QACell] = []
        for entry in sorted((p for p in root.iterdir() if p.is_dir()), key=lambda p: p.name.lower()):
            summary_file = entry / 'qa_summary.csv'
            rows = self._parse_summary(summary_file)
            cells.append(QACell(
                cell=entry.name,
                has_plan=any(x.name.endswith('_QaPlan.xlsx') for x in entry.glob('*_QaPlan.xlsx')),
                has_summary=summary_file.exists(),
                summary_rows=len(rows)
            ))
        return cells
    
    def get_defaults(self, project: str, subproject: str, cell: Optional[str], qa_type: str = 'quality') -> QADefaults:
        """Get default parameters for QA execution.
        
        Args:
            qa_type: 'quality' (default: quality/3_qa) or 'process' (release/process)
        """
        tp = TimingPaths(project, subproject)
        tp.ensure_release_process_dir()
        release_process_dir = tp.release_process_dir
        
        # Cell list file
        cell_list_file = release_process_dir / 'dwc_cells.lst'
        if not cell_list_file.exists():
            try:
                cell_list_file.write_text('')
            except Exception:
                pass
        
        # Header file
        header_file = release_process_dir / 'header_dummy.txt'
        if not header_file.exists():
            try:
                header_file.write_text('')
            except Exception:
                pass
        
        # Data release path
        data_release = tp.timing_root / 'release' / 'Postedit_libs'
        
        # Outdir
        outdir_path = tp.timing_root / 'release' / 'PostQA_libs'
        try:
            outdir_path.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass
        
        # Queue default
        queue = 'quick'
        
        # Run directory default based on qa_type
        run_dir = str(tp.qa_run_dir(qa_type))
        
        # Plan heuristic
        plan_file = self._infer_constraint_plan(cell or project)
        
        summary_path = str(self._qa_cell_root(project, subproject, cell) / 'qa_summary.csv') if cell else None
        
        return QADefaults(
            project=project,
            subproject=subproject,
            cell=cell,
            plan_file=plan_file,
            pt_version="2022.12-SP5",
            summary_path=summary_path,
            cell_list_file=str(cell_list_file),
            header_file=str(header_file),
            data_release=str(data_release),
            outdir=str(outdir_path),
            queue=queue,
            run_dir=run_dir,
        )
    
    def get_available_cells(self, data_release_path: str) -> List[str]:
        """Get list of cells from data release directory."""
        path = Path(data_release_path)
        if not path.exists() or not path.is_dir():
            return []
        
        try:
            cells = []
            for entry in sorted(path.iterdir(), key=lambda p: p.name.lower()):
                if entry.is_dir():
                    cells.append(entry.name)
            return cells
        except Exception:
            return []
    
    def get_summary(self, project: str, subproject: str, cell: str) -> QASummary:
        """Get QA summary for a specific cell."""
        root = self._qa_cell_root(project, subproject, cell)
        if not root.exists():
            return QASummary(project=project, subproject=subproject, cell=cell, rows=[], source=None)
        
        summary_file = root / 'qa_summary.csv'
        if not summary_file.exists():
            candidates = list(root.glob('*_qa_summary.csv'))
            summary_file = candidates[0] if candidates else None
        
        rows = self._parse_summary(summary_file) if summary_file and summary_file.exists() else []
        return QASummary(
            project=project,
            subproject=subproject,
            cell=cell,
            rows=rows,
            source=str(summary_file) if summary_file and summary_file.exists() else None
        )
    
    def run_qa(self, project: str, subproject: str, request: QARunRequest) -> QARunResult:
        """Execute QA checks."""
        tp = TimingPaths(project, subproject)
        
        # Determine run directory
        if request.run_dir and request.run_dir.strip():
            run_dir = Path(request.run_dir.strip())
        else:
            run_dir = tp.qa_default_run_dir
        
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Determine cell list file to use
        if request.cell_list_file and str(request.cell_list_file).strip():
            # Use user-provided path as-is; do not overwrite
            cell_list_file = Path(str(request.cell_list_file).strip())
            user_cell_list_note = f"[Cell List] Using user-provided file: {cell_list_file}"
        else:
            # Auto-generate under release/process
            process_dir = tp.release_process_dir
            process_dir.mkdir(parents=True, exist_ok=True)
            cell_list_file = process_dir / 'dwc_cells.lst'
            cell_list_file.write_text('\n'.join(request.selected_cells) + '\n')
            user_cell_list_note = f"[Cell List] Generated with {len(request.selected_cells)} cells: {', '.join(request.selected_cells)}"
        
        # Sanitize selected checks
        selected = [c for c in request.selected_checks if c in DISPLAY_CHECKS]
        effective_checks = list(dict.fromkeys(MANDATORY_CHECKS + selected))
        
        # Build command
        cmd = [
            "bin/python/TMQAallcells.py",
            "-celllist", str(cell_list_file),
            "-data", request.data_release,
            "-header", request.header_file,
            "-prj", request.project,
            "-qsub", request.queue,
            "-rel", request.release,
            "-outdir", request.outdir,
        ]
        if request.plan_file:
            cmd.extend(['-plan', request.plan_file])
        for chk in effective_checks:
            cmd.append(f'-{chk}')
        
        # Generate script
        script_path = run_dir / 'runall_qa.csh'
        script_content = self._generate_csh_script(cmd)
        script_path.write_text(script_content)
        
        try:
            script_path.chmod(0o755)
        except Exception:
            pass
        
        # Setup symlinks
        warnings = []
        symlink_output = ""
        try:
            svc = SymlinkService()
            symlink_result = svc.link_cell_tools(run_dir)
            symlink_output = f"[Symlink Setup] {symlink_result.note}\n"
            warnings.extend(symlink_result.warnings)
        except Exception as e:
            symlink_output = f"[Symlink Setup] Warning: Failed to create symlinks: {e}\n"
        
        # Create job
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            'status': 'pending',
            'stdout': symlink_output + user_cell_list_note + "\n",
            'stderr': '',
            'pid': None,
            'script_path': str(script_path),
            'command': ' '.join(cmd),
        }
        
        # Launch background execution
        def _run_job():
            try:
                self._jobs[job_id]['status'] = 'running'
                proc = subprocess.Popen(
                    [str(script_path)],
                    cwd=str(run_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self._jobs[job_id]['pid'] = proc.pid
                stdout, stderr = proc.communicate(timeout=3600)
                self._jobs[job_id]['stdout'] += stdout
                self._jobs[job_id]['stderr'] += stderr
                self._jobs[job_id]['status'] = 'completed' if proc.returncode == 0 else 'error'
            except Exception as e:
                self._jobs[job_id]['status'] = 'error'
                self._jobs[job_id]['stderr'] += f'\nError: {e}'
        
        threading.Thread(target=_run_job, daemon=True).start()
        
        return QARunResult(
            project=project,
            subproject=subproject,
            job_id=job_id,
            cmd=' '.join(cmd),
            started=True,
            working_dir=str(run_dir),
            script_path=str(script_path),
            effective_checks=effective_checks,
            warnings=warnings,
            note=f'Script generated at {script_path} (job_id={job_id}) with {len(request.selected_cells)} selected cells'
        )
    
    def get_job_status(self, job_id: str) -> Optional[QAJobStatus]:
        """Get status of a running QA job."""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        return QAJobStatus(
            job_id=job_id,
            status=job['status'],
            stdout=job['stdout'],
            stderr=job['stderr'],
            pid=job.get('pid'),
            script_path=job.get('script_path'),
            command=job['command']
        )
    
    # Helper methods
    def _qa_root(self, project: str, subproject: str) -> Path:
        return TimingPaths(project, subproject).qa_quality_root
    
    def _qa_cell_root(self, project: str, subproject: str, cell: str) -> Path:
        return TimingPaths(project, subproject).qa_cell_dir(cell)
    
    def _parse_summary(self, path: Path) -> List[QASummaryRow]:
        """Parse QA summary CSV file."""
        rows: List[QASummaryRow] = []
        if not path or not path.exists():
            return rows
        
        try:
            with path.open(newline='', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                for r in reader:
                    rows.append(QASummaryRow(
                        test=r.get('Test') or r.get('Check') or 'Unknown',
                        status=r.get('Status') or r.get('Result') or 'Unknown',
                        value=r.get('Value') or '',
                        detail=r.get('Detail') or r.get('Notes') or '',
                    ))
        except Exception:
            return []
        return rows
    
    def _infer_constraint_plan(self, cell_or_project: Optional[str]) -> str:
        """Infer constraint plan path based on project/cell name."""
        key = (cell_or_project or '').lower()
        
        if key.startswith('h3'):
            gen = 'gr_ucie3_v1'
        elif key.startswith('h2'):
            gen = 'gr_ucie2_v2'
        elif key.startswith('h1'):
            gen = 'gr_ucie'
        else:
            return ''
        
        return f"//wwcad/msip/projects/ucie/tb/{gen}/design/timing/plan/uciephy_constraint.xlsx"
    
    def _generate_csh_script(self, cmd: List[str]) -> str:
        """Generate CSH script from command."""
        if not cmd:
            return '#!/bin/csh\n'
        
        first = cmd[0]
        parts = cmd[1:]
        lines = ['#!/bin/csh', f'{first} \\']
        
        i = 0
        while i < len(parts):
            token = parts[i]
            is_last = i == len(parts) - 1
            
            if token.startswith('-') and i + 1 < len(parts) and not parts[i+1].startswith('-'):
                # flag with value
                lines.append(f"\t{token} {parts[i+1]}" + ('' if i+1 == len(parts)-1 else ' \\'))
                i += 2
            else:
                # Single flag
                lines.append(f"\t{token}" + ('' if is_last else ' \\'))
                i += 1
        
        return '\n'.join(lines) + '\n'
    
    def get_matrix_summary(self, project: str, subproject: str, run_dir: str) -> CellCheckMatrix:
        """Get QA matrix summary from brief.sum files in run directory."""
        run_path = Path(run_dir)
        if not run_path.exists() or not run_path.is_dir():
            return CellCheckMatrix(
                project=project,
                subproject=subproject,
                run_dir=run_dir,
                cell_names=[],
                check_items=[],
                status_matrix=[],
                cells_with_brief_sum=[],
                missing_cells=[]
            )
        
        # Scan for cell directories with brief.sum files
        cell_data: Dict[str, Dict[str, str]] = {}  # cell_name -> {check_name: status}
        all_check_items: set = set()
        cells_with_brief_sum: List[str] = []
        
        for cell_dir in sorted(run_path.iterdir(), key=lambda p: p.name.lower()):
            if not cell_dir.is_dir():
                continue
            
            brief_sum_file = cell_dir / 'brief.sum'
            if not brief_sum_file.exists():
                continue
            
            cell_name = cell_dir.name
            cells_with_brief_sum.append(cell_name)
            cell_checks = {}
            
            try:
                with brief_sum_file.open('r', encoding='utf-8', errors='replace') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Parse format: "check_name STATUS"
                        parts = line.split()
                        if len(parts) >= 2:
                            check_name = parts[0]
                            status = parts[1]
                            cell_checks[check_name] = status
                            all_check_items.add(check_name)
            except Exception:
                # Skip files that can't be read
                continue
            
            cell_data[cell_name] = cell_checks
        
        # Sort check items and cell names
        check_items = sorted(all_check_items)
        cell_names = sorted(cell_data.keys(), key=lambda s: s.lower())
        
        # Build status matrix: [check_index][cell_index] = status
        status_matrix: List[List[str]] = []
        for check_name in check_items:
            row = []
            for cell_name in cell_names:
                status = cell_data.get(cell_name, {}).get(check_name, '')
                row.append(status)
            status_matrix.append(row)
        
        return CellCheckMatrix(
            project=project,
            subproject=subproject,
            run_dir=run_dir,
            cell_names=cell_names,
            check_items=check_items,
            status_matrix=status_matrix,
            cells_with_brief_sum=cells_with_brief_sum,
            missing_cells=[]
        )
