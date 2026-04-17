"""Use cases for distributed task script generation."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List

from app.domain.distributed_task.entities import DistributedTaskConfig, RemoteHost
from app.domain.distributed_task.repositories import RemoteHostRepository


@dataclass
class GenerateDistributedTaskScriptInput:
    """Input for generating distributed task script."""
    task_type: str  # 'send', 'sim', 'get_back'
    folder_run_dir: str  # Local testbench directory (script will be created in parent)
    remote_dir: str  # Remote directory path
    remote_host: str  # Selected remote host (username@hostname)
    sim_command: str = "./runall.csh"  # Command to run remotely (relative to testbench folder)


@dataclass
class GenerateDistributedTaskScriptOutput:
    """Output from script generation."""
    script_path: str
    script_content: str
    note: str


class GenerateDistributedTaskScript:
    """Generate distributed task execution script (.csh file)."""
    
    def __init__(self, remote_host_repo: RemoteHostRepository):
        self.remote_host_repo = remote_host_repo
    
    def execute(self, inp: GenerateDistributedTaskScriptInput) -> GenerateDistributedTaskScriptOutput:
        """Generate the distributed task script in parent directory."""
        # Parse remote host
        if '@' in inp.remote_host:
            username, hostname = inp.remote_host.split('@', 1)
            remote_host = RemoteHost(hostname=hostname, username=username)
        else:
            raise ValueError(f"Invalid remote host format: {inp.remote_host}. Expected username@hostname")
        
        # Extract testbench name from folder_run_dir (last component of path)
        testbench_path = Path(inp.folder_run_dir)
        testbench_name = testbench_path.name
        
        # Script will be created in parent directory
        parent_dir = testbench_path.parent
        
        # Create config (keep sim_command as-is)
        config = DistributedTaskConfig(
            task_type=inp.task_type,
            local_dir=inp.folder_run_dir,
            remote_host=remote_host,
            remote_dir=inp.remote_dir,
            sim_command=inp.sim_command,
            local_result_dir=inp.folder_run_dir,
            testbench_name=testbench_name
        )
        
        # Build script content
        script_content = self._build_script_content(config)
        
        # Write script file in parent directory
        parent_dir.mkdir(parents=True, exist_ok=True)
        
        script_path = parent_dir / config.get_script_name()
        script_path.write_text(script_content)
        
        # Make executable
        try:
            script_path.chmod(0o755)
        except Exception:
            pass
        
        return GenerateDistributedTaskScriptOutput(
            script_path=str(script_path),
            script_content=script_content,
            note=f"Generated {config.get_script_name()}"
        )
    
    def _build_script_content(self, config: DistributedTaskConfig) -> str:
        """Build the .csh script content."""
        lines = [
            "#!/bin/csh -f",
            f"# Generated distributed task script: {config.task_type}",
            f"# Remote host: {config.remote_host.connection_string}",
            "",
            "./bin/python/sync_sim.py \\",
            f"  {config.get_sync_mode()} \\",
            f"  --local-dir {config.local_dir} \\",
            f"  --remote-host {config.remote_host.connection_string} \\",
            f"  --remote-dir {config.remote_dir} \\",
            f"  --sim-command \"{config.sim_command}\" \\",
            f"  --local-result-dir {config.local_result_dir or config.local_dir} \\",
            f"  --logfile {config.get_logfile_name()}",
            ""
        ]
        return "\n".join(lines)


class ListRemoteHosts:
    """List available remote hosts from configuration."""
    
    def __init__(self, remote_host_repo: RemoteHostRepository):
        self.remote_host_repo = remote_host_repo
    
    def execute(self) -> List[RemoteHost]:
        """Get list of remote hosts."""
        return self.remote_host_repo.get_remote_hosts()
