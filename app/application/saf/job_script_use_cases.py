"""Application use-cases for SAF job script generation & execution.

Split responsibilities:
* GenerateJobScript: purely builds a job script and writes (optional).
* RunJobScript: executes existing script via injected execution service.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from app.infrastructure.processes.job_execution_service import JobExecutionService, JobExecutionResult

# Formatting helpers inlined (legacy versions deleted from saf_service)
def _format_runall_command(*, cell: str, project: str, subproject: str,
                           hspice_version: str, finesim_version: str,
                           primesim_version: Optional[str], siliconsmart_version: str,
                           queue: str, netlist_type: str, pvt_list: Optional[str],
                           raw_lib_paths: Optional[str] = None, internal_saf: bool = False) -> str:
    lines = [
        "TimingCloseBeta.py -update",
        "bin/python/SAFplatform.py \\",
        f"        -cell {cell} \\",
        f"        -hspiceVersion {hspice_version} \\",
        f"        -finesimVersion {finesim_version} \\",
        f"        -primesimVersion {primesim_version} \\",
        f"        -siliconsmartVersion {siliconsmart_version} \\",
        f"        -queue {queue} \\",
        f"        -netlistType {netlist_type} \\",
        f"        -prj {project} \\",
    ]
    if pvt_list:
        lines.append(f"        -pvt_list \"{pvt_list}\" \\")
    if raw_lib_paths:
        lines.append(f"        -output {raw_lib_paths} \\")
    if internal_saf:
        lines.append("        -internalSAF \\")
    lines.append(f"        -rel {subproject}")
    return "\n".join(lines) + "\n"

def _format_nt_runall_command(*, cell_path: str, nt_option: Optional[str] = None, selected_pvts: Optional[List[str]] = None, raw_lib_paths: Optional[str] = None, bsub_args: Optional[str] = None) -> str:
    """Format NT job script content.

    Rules:
    * If selected_pvts provided -> use --sim "pvt1 pvt2 ..." (ignores nt_option)
    * Else if nt_option provided and non-empty -> append that option verbatim (e.g. --merge / --munge / --reload)
    * Else (Setup action) -> no extra option appended.
    """
    option_part = ""
    if selected_pvts:
        # When explicit PVT selection is provided, ignore nt_option per existing rules
        pvt_string = " ".join(selected_pvts)
        option_part = f' --sim "{pvt_string}"'
    elif nt_option and nt_option.strip():
        opt = nt_option.strip()
        option_part = f" {opt}"
        # Enhancement: when user triggers Merge OR Munge (conditional client-side) append --output <Raw Libs Path> if provided
        if opt in ("--merge", "--munge") and raw_lib_paths:
            option_part += f" --output {raw_lib_paths}"
    # Always include bsub args when provided (wrapped in quotes)
    bsub_part = f' --bsub-args "{bsub_args}"' if (bsub_args and bsub_args.strip()) else ""
    
    # Extract cell name from cell_path for job naming
    cell_name = Path(cell_path).name
    
    # Wrap the command with bsub for LSF job submission
    bsub_wrapper = f'bsub -Is -app quick -n 1 -M 100G -R "select[os_version= CS7.0] span[hosts=1] rusage[mem=10GB,scratch_free=5]" -J nt_job_{cell_name} '
    
    return f"#!/bin/csh -f\nTimingCloseBeta.py -update \n{bsub_wrapper}./bin/python/bbSimGuiNT_Batch/lib/run_all_preps.py --block_path {cell_path}{option_part}{bsub_part}\n"



@dataclass
class GenerateJobScriptInput:
    project: str
    subproject: str
    cell: str
    cell_type: str  # 'sis' or 'nt'
    hspice_version: Optional[str] = None
    finesim_version: Optional[str] = None
    primesim_version: Optional[str] = None
    siliconsmart_version: Optional[str] = None
    queue: Optional[str] = None
    netlist_type: Optional[str] = None
    pvt_list: Optional[str] = None
    selected_pvts: Optional[List[str]] = None
    raw_lib_paths: Optional[str] = None
    nt_option: Optional[str] = None
    internal_saf: bool = False
    bsub_args: Optional[str] = None
    script_name: str = 'runall.csh'
    write: bool = True  # if False, just return content
    base_root: Path = Path('.')  # root to resolve cell path relative to (injected for tests)


@dataclass
class GenerateJobScriptOutput:
    content: str
    script_path: Path
    bytes_written: int
    note: str
    exec_cmd: Optional[str] = None  # command that would be executed (for UX display)


class GenerateJobScript:
    def execute(self, inp: GenerateJobScriptInput) -> GenerateJobScriptOutput:
        # Determine cell root path
        if inp.cell_type == 'nt':
            cell_root = inp.base_root / 'design' / 'timing' / 'nt' / inp.cell
        else:
            cell_root = inp.base_root / 'design' / 'timing' / 'sis' / inp.cell
        cell_root.mkdir(parents=True, exist_ok=True)
        script_path = cell_root.parent / inp.script_name
        if inp.cell_type == 'nt':
            # For NT: empty / None nt_option should NOT fallback to '--merge'. Only append if explicitly provided.
            content = _format_nt_runall_command(cell_path=str(cell_root), nt_option=inp.nt_option, selected_pvts=inp.selected_pvts, raw_lib_paths=inp.raw_lib_paths, bsub_args=inp.bsub_args)
            exec_cmd = f"csh {script_path}"  # expected shell
        else:
            pvt_list_str = inp.pvt_list
            if inp.selected_pvts:
                pvt_list_str = ' '.join(inp.selected_pvts)
            content = _format_runall_command(
                cell=inp.cell,
                project=inp.project,
                subproject=inp.subproject,
                hspice_version=inp.hspice_version or '2023.12-1',
                finesim_version=inp.finesim_version or '2023.12-1',
                primesim_version=inp.primesim_version or '2023.12-1',
                siliconsmart_version=inp.siliconsmart_version or '2024.09-SP4',
                queue=inp.queue or 'normal',
                netlist_type=inp.netlist_type or 'lpe',
                pvt_list=pvt_list_str,
                raw_lib_paths=inp.raw_lib_paths,
                internal_saf=inp.internal_saf,
            ) + '\n'
            exec_cmd = f"csh {script_path}"  # expected shell
        bytes_written = 0
        if inp.write:
            script_path.write_text(content)
            try:
                import os
                os.chmod(script_path, 0o755)
            except Exception:
                pass
            bytes_written = script_path.stat().st_size
        note = 'Generated (dry-run)' if not inp.write else 'Generated'
        return GenerateJobScriptOutput(content=content, script_path=script_path, bytes_written=bytes_written, note=note, exec_cmd=exec_cmd)


@dataclass
class RunJobScriptInput:
    script_path: Path
    timeout: int = 300


@dataclass
class RunJobScriptOutput:
    return_code: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool
    note: Optional[str]


class RunJobScript:
    def __init__(self, execution: JobExecutionService):
        self._exec = execution

    def execute(self, inp: RunJobScriptInput) -> RunJobScriptOutput:
        result: JobExecutionResult = self._exec.run_script(inp.script_path, timeout=inp.timeout)
        return RunJobScriptOutput(
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            timed_out=result.timed_out,
            note=result.note,
        )
