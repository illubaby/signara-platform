"""Domain-specific exceptions for QC feature."""
class QCError(Exception):
    """Base class for QC domain errors."""

class QCPathError(QCError):
    """Raised when a QC path resolution or validation fails."""

class P4VQueryError(QCError):
    """Raised when a P4V query fails or returns invalid data."""

__all__ = ["QCError", "QCPathError", "P4VQueryError"]