"""Infrastructure implementation of TerminalCommandRunner using subprocess."""
from __future__ import annotations

import os
import subprocess
import time
from typing import Optional

from app.domain.terminal.entities import ExecResult
from app.domain.terminal.repositories import TerminalCommandRunner

MAX_OUTPUT_BYTES = 200_000
DEFAULT_SHELL = os.environ.get("SHELL", "bash")


class SubprocessTerminalCommandRunner(TerminalCommandRunner):
    def run(self, command: str, timeout: int, workdir: Optional[str]) -> ExecResult:  # type: ignore[override]
        cwd = workdir or os.getcwd()
        started = time.time()
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                executable=DEFAULT_SHELL if os.name != 'nt' else None,
            )
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            truncated = False
            if len(stdout) > MAX_OUTPUT_BYTES:
                stdout = stdout[:MAX_OUTPUT_BYTES] + f"\n...[truncated {len(stdout)-MAX_OUTPUT_BYTES} bytes]"
                truncated = True
            if len(stderr) > MAX_OUTPUT_BYTES:
                stderr = stderr[:MAX_OUTPUT_BYTES] + f"\n...[truncated {len(stderr)-MAX_OUTPUT_BYTES} bytes]"
                truncated = True
            ended = time.time()
            return ExecResult(
                command=command,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
                truncated=truncated,
                note=None if proc.returncode == 0 else "Non-zero exit code",
            )
        except subprocess.TimeoutExpired as te:  # pragma: no cover - timeout path
            ended = time.time()
            out = (te.stdout or '')[:MAX_OUTPUT_BYTES]
            err = (te.stderr or '')[:MAX_OUTPUT_BYTES] + f"\n[TIMED OUT after {timeout}s]"
            return ExecResult(
                command=command,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=None,
                stdout=out,
                stderr=err,
                truncated=False,
                note=f"Timed out after {timeout}s",
            )
        except Exception as e:  # pragma: no cover
            ended = time.time()
            return ExecResult(
                command=command,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=None,
                stdout="",
                stderr=str(e),
                truncated=False,
                note="Execution failed",
            )
