"""
Infrastructure layer: External application launcher implementation.

Implements the ExternalApplicationLauncher port for Windows, macOS, and Linux.
Uses OS-specific commands to open files with their default applications.
"""

import subprocess
import os
import platform
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class OSExternalApplicationLauncher:
    """
    Launch files with their default system applications.
    
    Supports:
    - Windows: Uses os.startfile()
    - macOS: Uses 'open' command
    - Linux: Uses 'xdg-open' command
    """
    
    def open_with_default_app(self, file_path: Path) -> None:
        """
        Open a file with its default OS application.
        
        Args:
            file_path: Path object pointing to the file to open
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the path is not a file
            PermissionError: If insufficient permissions
            RuntimeError: If the application launch fails
        """
        # Validate file exists
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Validate it's a file (not a directory)
        if not file_path.is_file():
            logger.error(f"Path is not a file: {file_path}")
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            system = platform.system()
            logger.info(f"Opening file with default app on {system}: {file_path}")
            
            if system == "Windows":
                # Windows: use subprocess with 'start' command to bring window to front
                # The 'start' command with empty title "" and file path will open and focus the window
                subprocess.run(
                    ['cmd', '/c', 'start', '', str(file_path)],
                    shell=False,
                    check=False  # Don't raise exception if window already open
                )
                
            elif system == "Darwin":  # macOS
                # macOS: use 'open' command
                subprocess.run(["open", str(file_path)], check=True)
                
            elif system == "Linux":
                # Linux: use 'xdg-open' command
                subprocess.run(["xdg-open", str(file_path)], check=True)
                
            else:
                raise RuntimeError(f"Unsupported operating system: {system}")
            
            logger.info(f"Successfully launched application for: {file_path.name}")
            
        except PermissionError as e:
            logger.error(f"Permission denied opening file: {file_path}")
            raise PermissionError(f"Insufficient permissions to open file: {file_path}") from e
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to launch application for {file_path}: {e}")
            raise RuntimeError(f"Failed to launch application: {e}") from e
            
        except Exception as e:
            logger.error(f"Unexpected error opening file {file_path}: {e}")
            raise RuntimeError(f"Failed to open file: {e}") from e


__all__ = ['OSExternalApplicationLauncher']
