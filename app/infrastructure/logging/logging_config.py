"""Central logging configuration.

Moved from app/logging_config.py to app/infrastructure/logging/logging_config.py per architecture guidelines.
Provides helper to configure structured logging early (in app factory).
"""
from __future__ import annotations

import logging
import sys
from typing import Optional


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with a simple structured format if not already configured."""
    if logging.getLogger().handlers:
        return
    handler = logging.StreamHandler(sys.stdout)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level.upper())
    root.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    return logging.getLogger(name or __name__)

__all__ = ["configure_logging", "get_logger"]
