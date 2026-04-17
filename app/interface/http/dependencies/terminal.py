"""Dependency providers for terminal feature."""
from __future__ import annotations

from functools import lru_cache

from app.application.terminal.use_cases import ExecuteTerminalCommand
from app.infrastructure.processes.terminal_command_runner import SubprocessTerminalCommandRunner


@lru_cache
def get_execute_terminal_command_uc() -> ExecuteTerminalCommand:
    runner = SubprocessTerminalCommandRunner()
    return ExecuteTerminalCommand(runner=runner)
