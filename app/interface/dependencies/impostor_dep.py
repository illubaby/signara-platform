"""Dependency injection factories for impostor functionality.

Provides use case instances with wired infrastructure dependencies.
"""

from functools import lru_cache
from app.application.impostor.use_cases import RunBsubWithImpostor, GetImpostorMapping
from app.infrastructure.impostor.credentials_repository_fs import CredentialsRepositoryFS
from app.infrastructure.impostor.command_executor_su import CommandExecutorSU


@lru_cache
def get_credentials_repository() -> CredentialsRepositoryFS:
    """Get singleton credentials repository instance."""
    return CredentialsRepositoryFS()


@lru_cache
def get_command_executor() -> CommandExecutorSU:
    """Get singleton command executor instance."""
    return CommandExecutorSU()


def get_run_bsub_with_impostor_uc() -> RunBsubWithImpostor:
    """Get RunBsubWithImpostor use case instance with dependencies."""
    return RunBsubWithImpostor(
        credentials_repo=get_credentials_repository(),
        command_executor=get_command_executor()
    )


def get_impostor_mapping_uc() -> GetImpostorMapping:
    """Get GetImpostorMapping use case instance."""
    return GetImpostorMapping()
