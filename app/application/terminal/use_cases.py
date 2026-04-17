"""Application use cases for terminal feature."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.domain.terminal.entities import ExecResult, CommandRejectedError
from app.domain.terminal.repositories import TerminalCommandRunner, is_command_safe


@dataclass
class ExecuteTerminalCommand:
    runner: TerminalCommandRunner
    default_timeout: int = 120

    def execute(self, command: str, timeout: Optional[int] = None, workdir: Optional[str] = None) -> ExecResult:
        if not is_command_safe(command):
            raise CommandRejectedError("Command rejected by safety policy")
        to = timeout or self.default_timeout
        return self.runner.run(command=command, timeout=to, workdir=workdir)
