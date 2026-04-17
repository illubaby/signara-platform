"""Domain repository protocols for impostor functionality.

These are port definitions - infrastructure will implement them.
"""

from typing import Protocol, Dict
from pathlib import Path


class CredentialsRepository(Protocol):
    """Protocol for loading encrypted credentials."""
    
    def load_credentials(self) -> Dict[str, str]:
        """Load and decrypt user credentials.
        
        Returns:
            Dictionary mapping usernames to passwords
            
        Raises:
            FileNotFoundError: If key or credentials file not found
            Exception: If decryption fails
        """
        ...
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """Verify that credentials work for a given username.
        
        Args:
            username: The username to verify
            password: The password for authentication
            
        Returns:
            True if credentials are valid
        """
        ...


class CommandExecutor(Protocol):
    """Protocol for executing commands as different users."""
    
    def execute_script(
        self,
        username: str,
        password: str,
        script_path: Path,
        cwd: Path | None = None
    ) -> tuple[bool, str]:
        """Execute a script as a different user.
        
        Args:
            username: The user to execute as
            password: The password for authentication
            script_path: Path to the script to execute
            cwd: Working directory for execution
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        ...
    
    def execute_command(
        self,
        username: str,
        password: str,
        command: list[str],
        cwd: Path | None = None
    ) -> tuple[bool, str, str | None, str | None]:
        """Execute a command as a different user.
        
        Args:
            username: The user to execute as
            password: The password for authentication
            command: Command and arguments as list
            cwd: Working directory for execution
            
        Returns:
            Tuple of (success: bool, message: str, job_id: str|None, full_command: str|None)
        """
        ...
