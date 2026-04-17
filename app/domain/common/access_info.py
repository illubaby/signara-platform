"""Domain entities for access information detection."""

from dataclasses import dataclass
from enum import Enum


class AccessType(str, Enum):
    """Type of access to the application."""
    LOCAL = "local"
    SSH_FORWARDED = "ssh_forwarded"
    REMOTE = "remote"


@dataclass(frozen=True)
class AccessInfo:
    """Information about how the application is being accessed."""
    access_type: AccessType
    host: str
    is_local: bool
    is_ssh_forwarded: bool
    description: str
