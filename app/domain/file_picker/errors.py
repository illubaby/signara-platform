"""Domain exceptions for file picker feature."""


class FilePickerError(Exception):
    """Base exception for file picker domain errors."""
    pass


class PathViolation(FilePickerError):
    """Raised when path validation fails."""
    pass


class AccessDenied(FilePickerError):
    """Raised when access to a path is denied."""
    pass


__all__ = [
    "FilePickerError",
    "PathViolation",
    "AccessDenied",
]
