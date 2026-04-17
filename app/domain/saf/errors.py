"""Domain-level SAF exceptions (Phase 1 minimal set)."""

class SafError(Exception):
    """Base class for SAF domain errors."""


class SafValidationError(SafError):
    pass


class SafNotFoundError(SafError):
    pass


class SafPerforceError(SafError):
    pass


class SafSyncError(SafError):
    pass

__all__ = [
    "SafError",
    "SafValidationError",
    "SafNotFoundError",
    "SafPerforceError",
    "SafSyncError",
]
