"""Port definitions for distributed task operations."""
from typing import Protocol, List
from .entities import RemoteHost


class RemoteHostRepository(Protocol):
    """Port for reading remote host configuration."""
    
    def get_remote_hosts(self) -> List[RemoteHost]:
        """Read remote hosts from configuration file (~/.remote_host.lst)."""
        ...
