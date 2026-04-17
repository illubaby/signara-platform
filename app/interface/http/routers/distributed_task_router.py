"""Interface layer: distributed task HTTP router."""
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from typing import List

from app.application.distributed_task.use_cases import (
    GenerateDistributedTaskScript,
    GenerateDistributedTaskScriptInput,
    ListRemoteHosts
)
from app.infrastructure.distributed_task.remote_host_repository_fs import RemoteHostRepositoryFS

router = APIRouter(prefix="/api/distributed-task", tags=["distributed_task"])


# ============ Schemas ============
class GenerateScriptRequest(BaseModel):
    task_type: str  # 'send', 'sim', 'get_back'
    folder_run_dir: str
    remote_dir: str
    remote_host: str  # username@hostname
    sim_command: str = "./runall.csh"


class GenerateScriptResponse(BaseModel):
    script_path: str
    script_content: str
    note: str


class RemoteHostResponse(BaseModel):
    hostname: str
    username: str
    connection_string: str


class CheckScriptsRequest(BaseModel):
    folder_run_dir: str


class CheckScriptsResponse(BaseModel):
    send_exists: bool
    sim_exists: bool
    get_back_exists: bool


# ============ Dependency Providers ============
def get_generate_script_uc() -> GenerateDistributedTaskScript:
    repo = RemoteHostRepositoryFS()
    return GenerateDistributedTaskScript(repo)


def get_list_remote_hosts_uc() -> ListRemoteHosts:
    repo = RemoteHostRepositoryFS()
    return ListRemoteHosts(repo)


# ============ Endpoints ============
@router.post("/generate-script", response_model=GenerateScriptResponse)
def generate_script(
    req: GenerateScriptRequest = Body(...),
    uc: GenerateDistributedTaskScript = Depends(get_generate_script_uc)
):
    """Generate distributed task script (.csh file)."""
    inp = GenerateDistributedTaskScriptInput(
        task_type=req.task_type,
        folder_run_dir=req.folder_run_dir,
        remote_dir=req.remote_dir,
        remote_host=req.remote_host,
        sim_command=req.sim_command
    )
    output = uc.execute(inp)
    return GenerateScriptResponse(
        script_path=output.script_path,
        script_content=output.script_content,
        note=output.note
    )


@router.get("/remote-hosts", response_model=List[RemoteHostResponse])
def list_remote_hosts(uc: ListRemoteHosts = Depends(get_list_remote_hosts_uc)):
    """Get list of available remote hosts from ~/.remote_host.lst."""
    hosts = uc.execute()
    return [
        RemoteHostResponse(
            hostname=host.hostname,
            username=host.username,
            connection_string=host.connection_string
        )
        for host in hosts
    ]


@router.post("/check-scripts", response_model=CheckScriptsResponse)
def check_scripts(req: CheckScriptsRequest = Body(...)):
    """Check which distributed task scripts exist in the parent folder.
    Scripts are named: <scriptname>_<testbench_name>.csh
    """
    from pathlib import Path
    
    folder_path = Path(req.folder_run_dir)
    testbench_name = folder_path.name
    parent_dir = folder_path.parent
    
    send_exists = (parent_dir / f"send_task_{testbench_name}.csh").exists()
    sim_exists = (parent_dir / f"sim_sent_task_{testbench_name}.csh").exists()
    get_back_exists = (parent_dir / f"get_back_{testbench_name}.csh").exists()
    
    return CheckScriptsResponse(
        send_exists=send_exists,
        sim_exists=sim_exists,
        get_back_exists=get_back_exists
    )
