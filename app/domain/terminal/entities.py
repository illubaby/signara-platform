"""Domain entities for terminal command execution.

Pure dataclasses / value objects with no framework dependencies.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExecResult:
    command: str
    started_at: float
    ended_at: float
    duration: float
    return_code: Optional[int]
    stdout: str
    stderr: str
    truncated: bool = False
    note: Optional[str] = None

    def is_success(self) -> bool:
        return self.return_code == 0 and self.note is None


class CommandRejectedError(ValueError):
    """Raised when a command is rejected by the safety policy."""
