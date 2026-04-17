"""Pydantic schemas for file picker HTTP interface."""
from pydantic import BaseModel, Field
from typing import List, Optional


class PickerEntrySchema(BaseModel):
    """Schema for a file/folder entry in the picker."""
    name: str
    path: str
    is_dir: bool
    is_symlink: bool = False
    size: Optional[int] = None
    modified_time: Optional[str] = None


class BrowseDirectoryRequest(BaseModel):
    """Request schema for browsing a directory."""
    path: str = Field(..., description="Directory path to browse")


class BrowseDirectoryResponse(BaseModel):
    """Response schema for browsing a directory."""
    current_path: str
    parent_path: str
    entries: List[PickerEntrySchema]


class ValidatePathRequest(BaseModel):
    """Request schema for path validation."""
    path: str = Field(..., description="Path to validate")


class ValidatePathResponse(BaseModel):
    """Response schema for path validation."""
    is_valid: bool
    is_directory: bool
    error_message: str = ""


__all__ = [
    "PickerEntrySchema",
    "BrowseDirectoryRequest",
    "BrowseDirectoryResponse",
    "ValidatePathRequest",
    "ValidatePathResponse",
]
