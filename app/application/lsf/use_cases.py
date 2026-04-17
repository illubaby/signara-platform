from dataclasses import dataclass
from app.domain.lsf.repositories import LSFJobRunner
from app.domain.lsf.entities import LSFJobExecution

@dataclass(frozen=True)
class RunBjobsInput:
    command: str
    timeout: int
    username: str | None = None

class RunBjobs:
    def __init__(self, runner: LSFJobRunner):
        self._runner = runner

    def execute(self, inp: RunBjobsInput) -> LSFJobExecution:
        cmd = inp.command.strip()
        if not cmd.startswith('bjobs'):
            raise ValueError("Only 'bjobs' commands are allowed")
        # Basic guard against dangerous shell expansions; keep simple for now
        for forbidden in [';', '&&', '|', '>', '>>', '$(', '`']:
            if forbidden in cmd:
                raise ValueError(f"Forbidden token in command: {forbidden}")
        return self._runner.run_bjobs(cmd, inp.timeout, inp.username)

__all__ = ['RunBjobs', 'RunBjobsInput']
