"""Domain entities for distributed task execution."""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class RemoteHost:
    """Remote host configuration."""
    hostname: str
    username: str
    
    @property
    def connection_string(self) -> str:
        """Return username@hostname format."""
        return f"{self.username}@{self.hostname}"


@dataclass(frozen=True)
class DistributedTaskConfig:
    """Configuration for distributed task execution."""
    task_type: str  # 'send', 'sim', 'get_back'
    local_dir: str
    remote_host: RemoteHost
    remote_dir: str
    sim_command: str = "./runall.csh"
    local_result_dir: Optional[str] = None
    testbench_name: Optional[str] = None
    
    def get_script_name(self) -> str:
        """Get script filename based on task type with testbench name suffix.
        Format: <scriptname>_<testbench_name>.csh
        """
        base_mapping = {
            'send': 'send_task',
            'sim': 'sim_sent_task',
            'get_back': 'get_back'
        }
        base_name = base_mapping.get(self.task_type, 'task')
        
        if self.testbench_name:
            return f"{base_name}_{self.testbench_name}.csh"
        return f"{base_name}.csh"
    
    def get_sync_mode(self) -> str:
        """Get sync mode flag based on task type."""
        mapping = {
            'send': '--sync-to-remote',
            'sim': '--run-simulation',
            'get_back': '--sync-from-remote'
        }
        return mapping.get(self.task_type, '--sync-to-remote')
    
    def get_logfile_name(self) -> str:
        """Get logfile name based on task type."""
        return f"{self.task_type}.log"
