from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


DEFAULT_TIMEOUT = 120


class ExecRequest(BaseModel):
    command: str = Field(..., description="Shell command to execute")
    timeout: int = Field(DEFAULT_TIMEOUT, ge=1, le=600)
    workdir: Optional[str] = Field(None, description="Working directory (optional)")


class ExecResponse(BaseModel):
    command: str
    started_at: float
    ended_at: float
    duration: float
    return_code: int | None
    stdout: str
    stderr: str
    truncated: bool = False
    note: str | None = None
