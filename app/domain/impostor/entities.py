"""Domain entities for impostor (user impersonation) functionality.

Pure business entities with no external dependencies.
"""

from dataclasses import dataclass
from typing import Dict


# Impostor mapping: UI name -> actual username
IMPOSTOR_MAP = {
    "Impostor1": "congdanh",
    "Impostor2": "thaison",
}


@dataclass(frozen=True)
class ImpostorUser:
    """Represents an impostor user configuration."""
    key: str  # e.g., "Impostor1"
    username: str  # e.g., "congdanh"
    
    @staticmethod
    def from_key(key: str) -> "ImpostorUser":
        """Create ImpostorUser from impostor key.
        
        Args:
            key: The impostor identifier (e.g., "Impostor1")
            
        Returns:
            ImpostorUser instance
            
        Raises:
            ValueError: If key is invalid
        """
        if key not in IMPOSTOR_MAP:
            raise ValueError(
                f"Invalid impostor key: {key}. Valid keys: {list(IMPOSTOR_MAP.keys())}"
            )
        
        return ImpostorUser(key=key, username=IMPOSTOR_MAP[key])
    
    @staticmethod
    def get_all() -> Dict[str, str]:
        """Get all impostor mappings.
        
        Returns:
            Dictionary mapping impostor keys to usernames
        """
        return IMPOSTOR_MAP.copy()


@dataclass(frozen=True)
class CommandResult:
    """Result of command execution."""
    success: bool
    message: str
    job_id: str | None = None
    full_command: str | None = None
