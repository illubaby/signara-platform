from fastapi import APIRouter, Body, Depends, HTTPException
from app.interface.http.schemas.lsf import LSFJobRequest, LSFJobResponse
from app.interface.http.dependencies import get_run_bjobs_uc
from app.application.lsf.use_cases import RunBjobs, RunBjobsInput

router = APIRouter(prefix="/api/lsf", tags=["lsf"])

@router.post("/bjobs", response_model=LSFJobResponse)
async def run_bjobs(req: LSFJobRequest = Body(...), uc: RunBjobs = Depends(get_run_bjobs_uc)):
    try:
        out = uc.execute(RunBjobsInput(command=req.command, timeout=req.timeout, username=req.username))
        return LSFJobResponse(**out.__dict__)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

__all__ = ["router"]
