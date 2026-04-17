"""Router for Jira task creation endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.application.jira.use_cases import CreateJiraBatch


router = APIRouter(prefix="/api/jira", tags=["jira"])


class JiraTaskSchema(BaseModel):
    """Schema for a single Jira task."""
    summary: str
    brief: str
    outcome: str
    assignee: str
    stakeholder: str
    labels: str
    due_date: str


class CreateJiraBatchRequest(BaseModel):
    """Request schema for creating Jira batch."""
    tasks: list[JiraTaskSchema]
    last_env: str = "prod"
    working_directory: Optional[str] = None


@router.post("/create-batch")
async def create_jira_batch(request: CreateJiraBatchRequest):
    """
    Create jira.json file and execute jirabatch.py script.
    
    Args:
        request: Contains tasks list and optional environment/directory settings
        
    Returns:
        Result of batch creation and execution
    """
    try:
        # Convert Pydantic models to dicts
        tasks_dict = [task.model_dump() for task in request.tasks]
        
        # Execute use case
        use_case = CreateJiraBatch(working_directory=request.working_directory)
        result = use_case.execute(tasks=tasks_dict, last_env=request.last_env)
        
        # Return full result including error details
        if not result["success"]:
            # Include all details in the error response
            raise HTTPException(
                status_code=500, 
                detail={
                    "message": result.get("message", "Unknown error"),
                    "error": result.get("error", ""),
                    "json_path": result.get("json_path", ""),
                    "command": result.get("command", ""),
                    "stdout": result.get("stdout", ""),
                    "stderr": result.get("stderr", ""),
                    "returncode": result.get("returncode", -1)
                }
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        # Catch any unexpected errors
        import traceback
        error_traceback = traceback.format_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "message": f"Unexpected error: {str(e)}",
                "error": str(e),
                "traceback": error_traceback
            }
        )


__all__ = ["router"]
