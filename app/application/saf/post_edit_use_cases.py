"""Post-Edit use-cases (Phase 8)

Encapsulate legacy `compute_defaults` and `run_post_edit` logic behind
application layer abstractions so routers & UI depend only on stable
interfaces. This allows eventual removal of the service functions.

Design notes:
 - Keep filesystem path derivation deterministic & side-effect free
   in GetPostEditDefaults.
 - Only RunPostEdit performs a subprocess call; injected executor
   makes it testable.
 - We intentionally do not model plan/reference heuristics here;
   routers may still add UI-specific selection rules.
 - Output truncation mirrors existing behavior (50k limit).

Contract overview:
 GetPostEditDefaultsInput(project, subproject, cell?) -> GetPostEditDefaultsOutput
 RunPostEditInput(project, subproject, cell, configfile, lib, plan, reformat, pt,
                  reference?, copy_reference, reorder, leakage, output?) -> RunPostEditOutput

Edge cases handled:
 - Missing SiS root or cell directory -> FileNotFoundError
 - Missing config file -> FileNotFoundError
 - Missing required parameters (lib/plan/pt) -> ValueError
 - Script resolution fallback when symlink not present.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import subprocess
import sys

from app.infrastructure.fs import project_root  # dynamic access to PROJECTS_BASE

SIS_SUBPATH = Path("design/timing/sis")
QUALITY_SUBPATH = Path("design/timing/quality/1_postedit")


@dataclass
class GetPostEditDefaultsInput:
    project: str
    subproject: str
    cell: Optional[str] = None


@dataclass
class GetPostEditDefaultsOutput:
    config_dir: str
    config_file: Optional[str]
    lib_path: str
    reference_path: str
    output_path: str


class GetPostEditDefaults:
    """Derive default filesystem paths for post-edit operations.

    Pure path computation; no I/O besides existence checks.
    """
    def execute(self, inp: GetPostEditDefaultsInput) -> GetPostEditDefaultsOutput:
        base = project_root.PROJECTS_BASE
        sis_root = base / inp.project / inp.subproject / SIS_SUBPATH
        config_file = None
        if inp.cell and (sis_root / inp.cell).is_dir():
            candidate = sis_root / inp.cell / f"{inp.cell}.cfg"
            if candidate.is_file():
                config_file = str(candidate)
        lib_path = base / inp.project / inp.subproject / "design" / "timing" / "release" / "raw_lib"
        output_path = base / inp.project / inp.subproject / "design" / "timing" / "release" / "Postedit_libs"
        return GetPostEditDefaultsOutput(
            config_dir=str(sis_root),
            config_file=config_file,
            lib_path=str(lib_path),
            reference_path=str(lib_path),  # reference path mirrors lib path (legacy behavior)
            output_path=str(output_path),
        )


@dataclass
class RunPostEditInput:
    project: str
    subproject: str
    cell: str
    configfile: str
    lib: Optional[str]
    plan: Optional[str]
    reformat: str
    pt: str
    reference: Optional[str] = None
    copy_reference: bool = False
    reorder: bool = False
    leakage: bool = False
    update: bool = False
    output: Optional[str] = None
    timeout: Optional[int] = None  # reserved for future async version


@dataclass
class RunPostEditOutput:
    started: bool
    note: str
    return_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    cmd: List[str]
    working_dir: str
    script_path: Optional[str] = None


class RunPostEdit:
    """Execute post-edit script synchronously and capture output.

    This mirrors legacy service logic but lives in application layer.
    Router remains responsible for symlink setup & UI heuristics.
    
    Now generates a runall.csh script file in the quality directory,
    making it easier for users to track and re-run commands.
    """
    
    def build_command(self, inp: RunPostEditInput) -> tuple[List[str], Path, str]:
        """Build the LSF bsub command and save it to runall.csh script.
        
        Returns:
            tuple: (command_list_to_execute, working_directory, script_path)
        """
        base = project_root.PROJECTS_BASE
        sis_root = base / inp.project / inp.subproject / SIS_SUBPATH
        quality_root = base / inp.project / inp.subproject / QUALITY_SUBPATH
        # Relaxed: allow running even if SiS root or specific cell directory is absent.
        # Users may provide external configfile paths and arbitrary cell names.
        # Original checks removed per user request.
        cfg_path = Path(inp.configfile)
        if not cfg_path.is_file():
            raise FileNotFoundError("Config file missing")
        # lib/plan can be omitted depending on workflow; only 'pt' is required
        if not inp.pt:
            raise ValueError("pt version required")

        script_name = "TimingCloseBeta.py"
        local_script = quality_root / script_name
        if local_script.exists():
            script_to_run = str(local_script)
        else:
            candidate = Path(__file__).resolve().parent.parent.parent / script_name
            script_to_run = str(candidate) if candidate.exists() else script_name

        interpreter = sys.executable or "python"
        try:
            sp = Path(script_to_run)
            if sp.is_file():
                with sp.open('r', errors='ignore') as fh:
                    first = fh.readline().strip()
                if first.startswith('#!'):
                    parts = first[2:].strip().split()
                    cand = parts[0]
                    if Path(cand).exists():
                        interpreter = cand
        except Exception:
            pass

        # Build the base python command
        python_cmd = [
            interpreter, script_to_run, "-postedit",
            "-cell", inp.cell,
            "-configfile", inp.configfile,
            "-pt", inp.pt,
        ]
        if inp.reformat:
            python_cmd.extend(["-reformat", inp.reformat])
        if inp.lib:
            python_cmd.extend(["-lib", inp.lib])
        if inp.plan:
            python_cmd.extend(["-plan", inp.plan])
        
        # Wrap with bsub for LSF job submission
        job_name = f"postedit_{inp.cell}_job"
        bsub_cmd = [
            "bsub",
            "-Is",
            "-app", "quick",
            "-n", "1",
            "-M", "100G",
            "-R", "span[hosts=1] rusage[mem=10GB,scratch_free=5]",
            "-J", job_name,
        ] + python_cmd
        if inp.output:
            bsub_cmd.extend(["-output", inp.output])
        if inp.copy_reference and inp.reference:
            bsub_cmd.extend(["-reference", inp.reference])
        if inp.reorder:
            bsub_cmd.append("-reorder")
        if inp.leakage:
            bsub_cmd.append("-leakage")
        if inp.update:
            bsub_cmd.append("-update")
        
        # Create runall.csh script in quality directory
        quality_root.mkdir(parents=True, exist_ok=True)
        script_path = quality_root / "runall.csh"
        
        # Format command for shell script
        # Escape special characters and quote arguments properly
        def shell_quote(arg: str) -> str:
            """Quote argument for csh if needed."""
            if ' ' in arg or any(c in arg for c in ['$', '`', '"', '!', '*', '?', '[', ']', '(', ')', '&', '|', ';', '<', '>', '\n', '\t']):
                # Escape special characters for csh
                escaped = arg.replace('\\', '\\\\')
                escaped = escaped.replace('$', '\\$')
                escaped = escaped.replace('`', '\\`')
                escaped = escaped.replace('!', '\\!')
                escaped = escaped.replace('"', '\\"')
                return f'"{escaped}"'
            return arg
        
        cmd_line = ' '.join(shell_quote(arg) for arg in bsub_cmd)
        
        # Write script with csh shebang
        script_content = f"""#!/bin/csh -f
# Auto-generated post-edit execution script
# Cell: {inp.cell}
# Project: {inp.project}/{inp.subproject}
# Generated: {Path(__file__).name}

{cmd_line}
"""
        
        script_path.write_text(script_content)
        script_path.chmod(0o755)  # Make executable
        
        # Return command to execute the script (simple csh invocation)
        exec_cmd = ["csh", str(script_path)]
        
        return exec_cmd, quality_root, str(script_path)
    
    def execute(self, inp: RunPostEditInput) -> RunPostEditOutput:
        """Execute post-edit with LSF and capture output synchronously.
        
        Generates runall.csh script and executes it.
        """
        cmd, quality_root, script_path = self.build_command(inp)
        
        try:
            proc = subprocess.run(cmd, cwd=str(quality_root), capture_output=True, text=True, check=False)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Unable to execute runall.csh script: {script_path}") from e
        except Exception as e:
            raise RuntimeError(f"Failed executing process: {e}") from e

        note = "Completed" if proc.returncode == 0 else f"Exited RC={proc.returncode}"
        def _trim(s: str, lim: int = 50000):
            return s if len(s) <= lim else s[:lim] + f"\n...[truncated {len(s)-lim} bytes]"
        return RunPostEditOutput(
            started=True,
            note=note,
            return_code=proc.returncode,
            stdout=_trim(proc.stdout or ''),
            stderr=_trim(proc.stderr or ''),
            cmd=cmd,
            working_dir=str(quality_root),
            script_path=script_path,
        )


__all__ = [
    "GetPostEditDefaults", "GetPostEditDefaultsInput", "GetPostEditDefaultsOutput",
    "RunPostEdit", "RunPostEditInput", "RunPostEditOutput",
]
