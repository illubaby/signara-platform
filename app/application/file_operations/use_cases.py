"""
Application layer: Use cases for file operations.

Contains business logic and orchestration for opening files with external applications.
No direct infrastructure or HTTP dependencies.
"""

from pathlib import Path
import logging

from app.domain.file_operations.repositories import ExternalApplicationLauncher, FileDownloadRepository

logger = logging.getLogger(__name__)


class OpenFileWithDefaultApp:
    """
    Use case: Open a file with its default system application.
    
    This is the simplest possible implementation - just takes a file path
    and opens it with the default app (e.g., Excel for .xlsx files).
    """
    
    def __init__(self, launcher: ExternalApplicationLauncher):
        """
        Args:
            launcher: Infrastructure implementation for launching apps
        """
        self.launcher = launcher
    
    def execute(self, file_path: str) -> dict[str, str]:
        """
        Execute the use case to open a file.
        
        Args:
            file_path: String path to the file (absolute or relative)
            
        Returns:
            Dict with:
                - status: "success" or "error"
                - message: Human-readable message
                
        Raises:
            ValueError: If file path is empty or invalid
            FileNotFoundError: If file doesn't exist
            PermissionError: If insufficient permissions
            RuntimeError: If launch fails
        """
        # Validate input
        if not file_path or not file_path.strip():
            logger.warning("Empty file path provided")
            raise ValueError("File path cannot be empty")
        
        # Convert to Path and resolve to absolute path
        try:
            path = Path(file_path).resolve()
        except Exception as e:
            logger.error(f"Invalid file path: {file_path}, error: {e}")
            raise ValueError(f"Invalid file path: {file_path}") from e
        
        logger.info(f"Use case: Opening file {path}")
        
        # Delegate to infrastructure
        self.launcher.open_with_default_app(path)
        
        return {
            "status": "success",
            "message": f"Successfully opened: {path.name}"
        }


__all__ = ['OpenFileWithDefaultApp']


class PrepareFileDownload:
    """Use case: Validate and prepare a file for browser download.

    Browser cannot directly invoke local Excel/Word when server runs remotely;
    we instead stream the file so the user's browser downloads it. This use case
    performs validation only and returns metadata for the router to build a
    streaming response (keeps HTTP concerns out of domain/app layers).
    """

    def __init__(self, repo: FileDownloadRepository):
        self.repo = repo

    def execute(self, file_path: str) -> dict[str, str]:
        """Validate path and return download metadata.

        Args:
            file_path: raw path from client (absolute or relative)
        Returns:
            dict with keys:
              - filename
              - absolute_path
        Raises:
            ValueError / FileNotFoundError / PermissionError propagated from repo
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        try:
            path_obj = Path(file_path)
        except Exception as e:  # pragma: no cover (rare invalid parse)
            raise ValueError(f"Invalid file path: {file_path}") from e
        validated = self.repo.validate_for_download(path_obj)
        logger.info(f"Prepared file for download: {validated}")
        return {"filename": validated.name, "absolute_path": str(validated)}


__all__.append('PrepareFileDownload')


class CountLibFilesInDirectory:
    """
    Use case: Count the number of .lib files in a directory, including its subdirectories.
    """

    def execute(self, dir_path: str) -> int:
        """
        Count the number of .lib files in the given directory and its subdirectories.

        Args:
            dir_path: Path to the directory to search.

        Returns:
            The number of .lib files found.

        Raises:
            ValueError: If the directory path is empty or invalid.
            FileNotFoundError: If the directory does not exist.
            NotADirectoryError: If the path is not a directory.
        """
        if not dir_path or not dir_path.strip():
            raise ValueError("Directory path cannot be empty")

        try:
            path = Path(dir_path).resolve()
        except Exception as e:
            raise ValueError(f"Invalid directory path: {dir_path}") from e

        if not path.exists():
            raise FileNotFoundError(f"Directory does not exist: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        # Count .lib files recursively
        lib_files_count = sum(1 for _ in path.rglob("*.lib"))
        logger.info(f"Found {lib_files_count} .lib files in directory: {path}")

        return lib_files_count


__all__.append('CountLibFilesInDirectory')


class CreateFileSimple:
    """Very simple file creation use case.

    Creates a file if it does not exist. Returns True if created, False if it already existed.
    NOTE: Direct filesystem access placed here per user request (normally would live in infrastructure layer).
    """

    def execute(self, dir_path: str, filename: str, content: str | None = None) -> bool:
        if not dir_path or not filename:
            raise ValueError("dir_path and filename are required")
        path = Path(dir_path).expanduser().resolve()
        path.mkdir(parents=True, exist_ok=True)
        file_path = path / filename
        if file_path.exists():
            return False
        # Create file with optional content
        file_path.write_text(content or "")
        return True

__all__.append('CreateFileSimple')


class ReadFileContent:
    """Read the entire content of a text file."""

    def execute(self, file_path: str) -> str:
        """Read file content.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
            
        Raises:
            ValueError: If path is empty or invalid
            FileNotFoundError: If file doesn't exist
            PermissionError: If insufficient permissions
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        
        try:
            path = Path(file_path).expanduser().resolve()
        except Exception as e:
            raise ValueError(f"Invalid file path: {file_path}") from e
        
        if not path.exists():
            raise FileNotFoundError(f"File does not exist: {path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {path}")
        
        logger.info(f"Reading file: {path}")
        return path.read_text(encoding='utf-8')

__all__.append('ReadFileContent')


class WriteFileContent:
    """Write content to a text file, creating it if necessary."""

    def execute(self, file_path: str, content: str) -> bool:
        """Write content to file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            
        Returns:
            True if successful
            
        Raises:
            ValueError: If path is empty or invalid
            PermissionError: If insufficient permissions
        """
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        
        if content is None:
            content = ""
        
        try:
            path = Path(file_path).expanduser().resolve()
        except Exception as e:
            raise ValueError(f"Invalid file path: {file_path}") from e
        
        # Create parent directories if needed
        path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Writing file: {path}")
        path.write_text(content, encoding='utf-8')
        return True

__all__.append('WriteFileContent')
