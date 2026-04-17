from pydantic import BaseModel, Field
from typing import Optional

class LSFJobRequest(BaseModel):
    command: str = Field(..., description="LSF command to execute (must start with bjobs)")
    timeout: int = Field(30, ge=1, le=120)
    username: Optional[str] = Field(None, description="Username to query jobs for (optional)")

class LSFJobResponse(BaseModel):
    command: str
    started_at: float
    ended_at: float
    duration: float
    return_code: Optional[int]
    stdout: str
    stderr: str
    truncated: bool
    note: Optional[str] = None

__all__ = ['LSFJobRequest', 'LSFJobResponse']
