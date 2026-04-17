"""Domain-specific errors for the Explorer feature.

These exceptions remain framework-agnostic. The Interface (HTTP) layer
is responsible for translating them into HTTP responses.
"""
from __future__ import annotations

class ExplorerError(Exception):
    """Base type for all explorer domain errors."""

class PathViolation(ExplorerError):
    """Raised when a provided relative path is invalid or escapes root."""

class PolicyViolation(ExplorerError):
    """Raised when a write or read operation violates a configured policy."""

class FileNotFoundDomain(ExplorerError):
    """Raised when a requested file does not exist."""

__all__ = [
    "ExplorerError",
    "PathViolation",
    "PolicyViolation",
    "FileNotFoundDomain",
]
