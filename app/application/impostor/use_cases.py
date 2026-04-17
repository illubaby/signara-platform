"""Use cases for impostor (user impersonation) functionality.

Orchestrates domain entities with infrastructure repositories.
"""

from pathlib import Path
from app.domain.impostor.entities import ImpostorUser, CommandResult
from app.domain.impostor.repositories import CredentialsRepository, CommandExecutor


class RunBsubWithImpostor:
    """Use case for running bsub commands as an impostor user."""
    
    def __init__(
        self,
        credentials_repo: CredentialsRepository,
        command_executor: CommandExecutor
    ):
        """Initialize with repository dependencies.
        
        Args:
            credentials_repo: Repository for loading credentials
            command_executor: Executor for running commands
        """
        self.credentials_repo = credentials_repo
        self.command_executor = command_executor
    
    def execute(
        self,
        impostor_key: str,
        bsub_cmd: list,
        cwd: Path | None = None
    ) -> CommandResult:
        """Run a bsub command as an impostor user.
        
        Args:
            impostor_key: The impostor identifier (e.g., "Impostor1", "Impostor2")
            bsub_cmd: The bsub command as a list of arguments
            cwd: Working directory for execution (optional)
            
        Returns:
            CommandResult with execution status
        """
        # Validate impostor key and get user
        try:
            impostor_user = ImpostorUser.from_key(impostor_key)
        except ValueError as e:
            return CommandResult(success=False, message=str(e))
        
        # Load credentials
        try:
            credentials = self.credentials_repo.load_credentials()
        except Exception as e:
            return CommandResult(success=False, message=f"Failed to load credentials: {e}")
        
        # Get password for impostor
        impostor_password = credentials.get(impostor_user.username)
        if not impostor_password:
            return CommandResult(
                success=False,
                message=f"Password for {impostor_user.username} not found in credentials"
            )
        
        # Verify su works
        if not self.credentials_repo.verify_credentials(impostor_user.username, impostor_password):
            return CommandResult(
                success=False,
                message=f"Failed to verify credentials for {impostor_user.username}"
            )
        
        # Execute via command executor
        success, message, job_id, full_cmd = self.command_executor.execute_command(
            username=impostor_user.username,
            password=impostor_password,
            command=bsub_cmd,
            cwd=cwd
        )
        
        return CommandResult(
            success=success,
            message=message,
            job_id=job_id,
            full_command=full_cmd
        )


class GetImpostorMapping:
    """Use case for retrieving impostor mappings."""
    
    def execute(self) -> dict[str, str]:
        """Get all impostor mappings.
        
        Returns:
            Dictionary mapping impostor keys to usernames
        """
        return ImpostorUser.get_all()
