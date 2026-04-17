"""FastAPI dependency providers for File Picker use cases.

Central place for wiring infrastructure into application layer.
"""
from __future__ import annotations

from app.application.file_picker.use_cases import BrowseDirectory, ValidatePath


def get_browse_directory_use_case() -> BrowseDirectory:
    """Get the BrowseDirectory use case with injected dependencies.
    
    Note: Infrastructure repository implementation is not included in this commit.
    You'll need to implement FilePickerRepositoryFS in infrastructure layer.
    """
    # TODO: Replace this with actual repository implementation
    # from app.infrastructure.file_picker.fs_repository import FilePickerRepositoryFS
    # repo = FilePickerRepositoryFS()
    # return BrowseDirectory(repo)
    
    # Temporary mock for testing the interface layer
    from app.domain.file_picker.repositories import FilePickerRepository
    from app.domain.file_picker.models import PickerPath, PickerEntry
    from pathlib import Path
    from typing import List
    
    class MockFilePickerRepository:
        """Temporary mock repository for testing."""
        
        def list_directory(self, path: PickerPath) -> List[PickerEntry]:
            """List directory contents."""
            import os
            from datetime import datetime
            
            path_obj = path.as_path()
            if not path_obj.exists():
                from app.domain.file_picker.errors import PathViolation
                raise PathViolation(f"Path does not exist: {path.value}")
            
            if not path_obj.is_dir():
                from app.domain.file_picker.errors import PathViolation
                raise PathViolation(f"Path is not a directory: {path.value}")
            
            entries = []
            try:
                for item in path_obj.iterdir():
                    try:
                        stat = item.stat()
                        size = stat.st_size if item.is_file() else None
                        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        entries.append(PickerEntry(
                            name=item.name,
                            path=str(item),
                            is_dir=item.is_dir(),
                            is_symlink=item.is_symlink(),
                            size=size,
                            modified_time=mtime
                        ))
                    except (PermissionError, OSError):
                        # Skip items we can't access
                        continue
            except PermissionError:
                from app.domain.file_picker.errors import AccessDenied
                raise AccessDenied(f"Access denied to: {path.value}")
            
            return entries
        
        def validate_path(self, path: PickerPath) -> bool:
            """Validate that a path exists and is accessible."""
            try:
                path_obj = path.as_path()
                return path_obj.exists()
            except (PermissionError, OSError):
                return False
    
    repo = MockFilePickerRepository()
    return BrowseDirectory(repo)


def get_validate_path_use_case() -> ValidatePath:
    """Get the ValidatePath use case with injected dependencies.
    
    Note: Infrastructure repository implementation is not included in this commit.
    You'll need to implement FilePickerRepositoryFS in infrastructure layer.
    """
    # TODO: Replace this with actual repository implementation
    # from app.infrastructure.file_picker.fs_repository import FilePickerRepositoryFS
    # repo = FilePickerRepositoryFS()
    # return ValidatePath(repo)
    
    # Temporary mock for testing the interface layer
    from app.domain.file_picker.repositories import FilePickerRepository
    from app.domain.file_picker.models import PickerPath, PickerEntry
    from pathlib import Path
    from typing import List
    
    class MockFilePickerRepository:
        """Temporary mock repository for testing."""
        
        def list_directory(self, path: PickerPath) -> List[PickerEntry]:
            """List directory contents."""
            import os
            from datetime import datetime
            
            path_obj = path.as_path()
            if not path_obj.exists():
                from app.domain.file_picker.errors import PathViolation
                raise PathViolation(f"Path does not exist: {path.value}")
            
            if not path_obj.is_dir():
                from app.domain.file_picker.errors import PathViolation
                raise PathViolation(f"Path is not a directory: {path.value}")
            
            entries = []
            try:
                for item in path_obj.iterdir():
                    try:
                        stat = item.stat()
                        size = stat.st_size if item.is_file() else None
                        mtime = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        entries.append(PickerEntry(
                            name=item.name,
                            path=str(item),
                            is_dir=item.is_dir(),
                            is_symlink=item.is_symlink(),
                            size=size,
                            modified_time=mtime
                        ))
                    except (PermissionError, OSError):
                        # Skip items we can't access
                        continue
            except PermissionError:
                from app.domain.file_picker.errors import AccessDenied
                raise AccessDenied(f"Access denied to: {path.value}")
            
            return entries
        
        def validate_path(self, path: PickerPath) -> bool:
            """Validate that a path exists and is accessible."""
            try:
                path_obj = path.as_path()
                return path_obj.exists()
            except (PermissionError, OSError):
                return False
    
    repo = MockFilePickerRepository()
    return ValidatePath(repo)


__all__ = [
    "get_browse_directory_use_case",
    "get_validate_path_use_case",
]
