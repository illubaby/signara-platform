"""
Interface layer: Pydantic schemas for file operations API.

Request and response models for HTTP endpoints.
"""

from pydantic import BaseModel, Field, field_validator


class OpenFileRequest(BaseModel):
    """Request to open a file with default application."""
    
    file_path: str = Field(
        ..., 
        description="Path to the file to open (absolute or relative)",
        examples=["C:\\path\\to\\file.xlsx", "/home/user/document.xlsx"]
    )
    
    @field_validator('file_path')
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that file path is not empty."""
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()


class OpenFileResponse(BaseModel):
    """Response from opening a file."""
    
    status: str = Field(
        ..., 
        description="Status of the operation",
        examples=["success", "error"]
    )
    message: str = Field(
        ..., 
        description="Human-readable message about the operation",
        examples=["Successfully opened: file.xlsx", "File not found"]
    )


__all__ = ['OpenFileRequest', 'OpenFileResponse']
