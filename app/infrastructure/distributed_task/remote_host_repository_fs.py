"""Infrastructure: remote host configuration reader."""
from pathlib import Path
from typing import List
import getpass

from app.domain.distributed_task.entities import RemoteHost
from app.domain.distributed_task.repositories import RemoteHostRepository


class RemoteHostRepositoryFS(RemoteHostRepository):
    """Read remote hosts from ~/.remote_host.lst file."""
    
    def get_remote_hosts(self) -> List[RemoteHost]:
        """Read remote hosts from configuration file."""
        config_path = Path.home() / ".remote_host.lst"
        
        if not config_path.exists():
            # Return empty list if config doesn't exist
            return []
        
        hosts = []
        username = getpass.getuser()
        
        try:
            content = config_path.read_text(encoding='utf-8')
            for line in content.splitlines():
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse format: hostname or username@hostname
                if '@' in line:
                    user, hostname = line.split('@', 1)
                    hosts.append(RemoteHost(hostname=hostname.strip(), username=user.strip()))
                else:
                    # Use current username if not specified
                    hosts.append(RemoteHost(hostname=line, username=username))
        except Exception as e:
            # Log error but return what we have
            print(f"Warning: Error reading remote host config: {e}")
        
        return hosts
