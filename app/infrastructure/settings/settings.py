"""Application settings (centralized configuration).

Moved from app/settings.py to app/infrastructure/settings/settings.py per architecture guidelines.
Uses Pydantic Settings so environment variables can override defaults.
Environment variable prefix: TIMING_
"""
from __future__ import annotations

from functools import lru_cache
from typing import List
from pydantic import Field
try:
    from pydantic_settings import BaseSettings  # Pydantic >=2 separate package
except ImportError:  # Fallback to classic BaseSettings if package missing
    from pydantic import BaseSettings  # type: ignore


class Settings(BaseSettings):
    environment: str = Field("local", description="Execution environment tag (local/dev/prod)")
    cache_ttl_seconds: int = Field(30, ge=1, le=3600, description="Default TTL for small in-memory caches")
    enable_job_execution: bool = Field(True, description="Allow running external job scripts (set False to disable)")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins")
    log_level: str = Field("INFO", description="Logging level (DEBUG/INFO/WARNING/ERROR)")
    reload: bool = Field(
        False,
        description=(
            "Enable uvicorn auto-reload. Default False to avoid 'OS file watch limit' errors on large workspaces."
        ),
    )
    reload_mode: str = Field(
        "auto",
        description="Reload strategy: auto|poll|none. 'poll' forces polling (lower FD usage). 'none' disables reload.",
    )
    reload_excludes: List[str] = Field(
        default_factory=lambda: [
            "*.pyc",
            "__pycache__",
            "timing-app/node_modules/*",  # large frontend deps tree – exclude to avoid watch limit
        ],
        description="Glob patterns to exclude from reload watching.",
    )
    auto_open_browser: bool = Field(
        True,
        description="Automatically open a web browser to the app after startup (skips on headless Linux)",
    )

    static_cache_control: str = Field(
        "no-cache",
        description=(
            "Cache-Control header to apply to /static/* responses. "
            "Use 'no-cache' (default) to avoid needing hard refresh during development; "
            "override with TIMING_STATIC_CACHE_CONTROL if desired."
        ),
    )
    writable_ext_allow: List[str] = Field(
        default_factory=lambda: [
            ".txt", ".log", ".cfg", ".tcl", ".csh", ".sh", ".csv", ".md", ".json", ".yml", ".yaml"
        ],
        description="Extensions allowed for editing via explorer (lowercase, leading dot)",
    )
    writable_ext_block: List[str] = Field(
        default_factory=lambda: [
            ".py"  # prevent accidental modification of application/runtime code
        ],
        description="Explicit extension blocklist even if present in allowlist",
    )
    explorer_max_write_bytes: int = Field(
        512 * 1024,
        ge=1024,
        le=5 * 1024 * 1024,
        description="Max file size allowed for write operations through explorer",
    )
    audit_explorer_writes: bool = Field(
        True,
        description="If true log each explorer write (path, size, created flag)",
    )

    class Config:
        env_prefix = "TIMING_"
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance so we don't rebuild for every import."""
    return Settings()

__all__ = ["Settings", "get_settings"]
