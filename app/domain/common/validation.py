"""Domain validation utilities for path components and names.

Pure domain logic with no framework dependencies.
"""
from __future__ import annotations

import re

_COMP_RE = re.compile(r"^[A-Za-z0-9._-]+$")


class ValidationError(Exception):
    """Raised when domain validation fails."""
    pass


def validate_component(name: str, field: str = "component") -> None:
    """Validate a single path component (project name, cell name, etc.).

    Args:
        name: The component name to validate
        field: Description of the field being validated (for error messages)

    Raises:
        ValidationError: If the name is invalid

    Accepts alphanumeric characters, dots, underscores, and dashes.
    """
    if not name or not _COMP_RE.fullmatch(name):
        raise ValidationError(f"Invalid {field}: {name!r}")


__all__ = ["validate_component", "ValidationError"]
