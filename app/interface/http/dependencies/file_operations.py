"""
Interface layer: Dependency injection providers for file operations.

Factory functions to create use cases with their dependencies wired up.
"""

from app.application.file_operations.use_cases import OpenFileWithDefaultApp, PrepareFileDownload
from app.infrastructure.processes.external_app_launcher import OSExternalApplicationLauncher
from app.infrastructure.fs.file_download_repository_fs import FileDownloadRepositoryFS


def get_open_file_use_case() -> OpenFileWithDefaultApp:
    """Factory for OpenFileWithDefaultApp use case."""
    launcher = OSExternalApplicationLauncher()
    return OpenFileWithDefaultApp(launcher=launcher)


def get_prepare_file_download_use_case() -> PrepareFileDownload:
    """Factory for PrepareFileDownload use case."""
    repo = FileDownloadRepositoryFS()
    return PrepareFileDownload(repo=repo)


__all__ = ['get_open_file_use_case', 'get_prepare_file_download_use_case']
