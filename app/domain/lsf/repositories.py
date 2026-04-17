from typing import Protocol, Optional
from .entities import LSFJobExecution

class LSFJobRunner(Protocol):
    def run_bjobs(self, command: str, timeout: int, username: Optional[str] = None) -> LSFJobExecution: ...
