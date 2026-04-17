"""
Domain layer: Port definitions for external application launching.

This module defines the contract (Protocol) for launching external applications.
No framework dependencies, pure business interface definition.
"""

from typing import Protocol
from pathlib import Path


class ExternalApplicationLauncher(Protocol):
    """Port for launching external applications with files."""

    def open_with_default_app(self, file_path: Path) -> None:  # pragma: no cover (simple delegation)
        """Open a file with its default system application."""
        ...


class FileDownloadRepository(Protocol):
    """Port for preparing a file for download to a remote client.

    The server runs on (likely) Linux; the browser may be on Windows via SSH tunnel.
    We cannot "open" the file on the client directly from the server. Instead we
    expose a secure validated path through a download endpoint so the browser
    downloads it and the user's OS can auto-open (depending on browser settings).
    """

    def validate_for_download(self, file_path: Path) -> Path:
        """Validate the requested file and return an absolute path.

        Must ensure:
          * Exists
          * Is a regular file (not dir)
          * Readable by server process

        Raises:
            FileNotFoundError: file does not exist
            ValueError: not a file or path outside allowed roots (future hardening)
            PermissionError: unreadable
        Returns:
            Absolute Path ready for streaming to client
        """
        ...

