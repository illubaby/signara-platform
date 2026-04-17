from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class LSFJobExecution:
    command: str
    started_at: float
    ended_at: float
    duration: float
    return_code: Optional[int]
    stdout: str
    stderr: str
    truncated: bool
    note: Optional[str] = None
