"""Infrastructure service for executing SAF job scripts.

Provides a thin wrapper around subprocess.run with timeout handling and
stdout/stderr truncation so upper layers don't repeat this logic.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence
import subprocess
import shutil


@dataclass
class JobExecutionResult:
    cmd: Sequence[str]
    cwd: str
    return_code: Optional[int]
    stdout: str
    stderr: str
    timed_out: bool = False
    note: Optional[str] = None


class JobExecutionService:
    def __init__(self, truncate_limit: int = 50000):
        self._truncate_limit = truncate_limit

    def run_script(self, script_path: Path, timeout: int = 300) -> JobExecutionResult:
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        # Prefer csh, fallback to bash
        if shutil.which("csh"):
            cmd = ["csh", str(script_path)]
        else:
            cmd = ["bash", str(script_path)]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(script_path.parent),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = self._truncate(proc.stdout or "")
            stderr = self._truncate(proc.stderr or "")
            note = "OK" if proc.returncode == 0 else f"Exited {proc.returncode}"
            return JobExecutionResult(cmd=cmd, cwd=str(script_path.parent), return_code=proc.returncode, stdout=stdout, stderr=stderr, note=note)
        except subprocess.TimeoutExpired as te:
            stdout = self._truncate((getattr(te, "stdout", None) or ""))
            stderr = self._truncate((getattr(te, "stderr", None) or ""))
            return JobExecutionResult(cmd=cmd, cwd=str(script_path.parent), return_code=None, stdout=stdout, stderr=stderr, timed_out=True, note=f"Timed out after {timeout}s")

    def _truncate(self, s: str) -> str:
        lim = self._truncate_limit
        return s if len(s) <= lim else s[:lim] + f"\n...[truncated {len(s)-lim} bytes]"
