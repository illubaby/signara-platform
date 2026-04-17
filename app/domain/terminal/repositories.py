"""Ports (protocols) for terminal command execution.

Application layer depends on these protocols; infrastructure supplies concrete implementations.
"""
from __future__ import annotations

from typing import Protocol
from .entities import ExecResult


class TerminalCommandRunner(Protocol):
    def run(self, command: str, timeout: int, workdir: str | None) -> ExecResult:  # pragma: no cover - protocol
        ...


SAFE_PREFIXES: list[str] = [
    "ls", "pwd", "echo", "cat", "head", "tail", "grep", "find", "df", "du", "whoami", "uname",
    "env", "printenv", "which", "date"
]

BANNED_COMMANDS: set[str] = {"rm", "shutdown", "reboot", "halt", "poweroff", "mkfs", "dd", ":(){:|:&};:"}

def is_command_safe(command: str) -> bool:
    """Very lightweight safety policy.

    Intentionally simple (no shell parsing of pipes/redirects). If the first token is in SAFE_PREFIXES
    we allow it; otherwise ensure it is not explicitly banned.
    """
    import shlex
    try:
        parts = shlex.split(command)
    except Exception:
        return False
    if not parts:
        return False
    first = parts[0]
    if first in SAFE_PREFIXES:
        return True
    if first in BANNED_COMMANDS:
        return False
    return True
