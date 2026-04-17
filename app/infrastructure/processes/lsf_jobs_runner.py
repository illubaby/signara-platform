import subprocess, time
from typing import Optional
from app.domain.lsf.entities import LSFJobExecution
from app.domain.lsf.repositories import LSFJobRunner

MAX_OUTPUT_BYTES = 200_000
DEFAULT_TIMEOUT = 30

class SubprocessLSFJobRunner(LSFJobRunner):
    def run_bjobs(self, command: str, timeout: int, username: Optional[str] = None) -> LSFJobExecution:
        started = time.time()
        raw_cmd = command.strip()
        # Auto-augment plain 'bjobs'
        if raw_cmd == 'bjobs':
            command = 'bjobs -o "jobid:8 user:12 stat:6 queue:15 from_host:25 exec_host:30 job_name:40 submit_time:20"'
            if username:
                command += f' -u {username}'
        try:
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = proc.stdout or ''
            stderr = proc.stderr or ''
            truncated = False
            if len(stdout) > MAX_OUTPUT_BYTES:
                stdout = stdout[:MAX_OUTPUT_BYTES] + f"\n...[truncated {len(stdout) - MAX_OUTPUT_BYTES} bytes]"
                truncated = True
            if len(stderr) > MAX_OUTPUT_BYTES:
                stderr = stderr[:MAX_OUTPUT_BYTES] + f"\n...[truncated {len(stderr) - MAX_OUTPUT_BYTES} bytes]"
                truncated = True
            ended = time.time()
            return LSFJobExecution(
                command=raw_cmd,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
                truncated=truncated,
                note=None if proc.returncode == 0 else 'Command returned non-zero exit code',
            )
        except subprocess.TimeoutExpired as te:
            ended = time.time()
            out = (te.stdout.decode() if te.stdout else '')[:MAX_OUTPUT_BYTES]
            err = (te.stderr.decode() if te.stderr else '')[:MAX_OUTPUT_BYTES] + '\n[TIMED OUT]'
            return LSFJobExecution(
                command=raw_cmd,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=None,
                stdout=out,
                stderr=err,
                truncated=False,
                note=f'Timed out after {timeout}s',
            )
        except Exception as e:
            ended = time.time()
            return LSFJobExecution(
                command=raw_cmd,
                started_at=started,
                ended_at=ended,
                duration=ended - started,
                return_code=None,
                stdout='',
                stderr=str(e),
                truncated=False,
                note='Execution failed',
            )

__all__ = ['SubprocessLSFJobRunner', 'MAX_OUTPUT_BYTES', 'DEFAULT_TIMEOUT']
