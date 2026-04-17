"""Filesystem project root resolution.

Moved from app/config.py to app/infrastructure/fs/project_root.py per architecture guidelines.
Provides PROJECTS_BASE path used throughout infrastructure/routers to locate project data.
"""
from __future__ import annotations

import os
import getpass
from pathlib import Path

_WINDOWS_DEFAULTS = [
    "C:/Users/{user}/Perforce/{user}_SNPS/projects/ucie",
    "C:/Users/{user}/Perforce/{user}_SNPS/wwcad/msip/projects/ucie",
]

def _linux_candidate() -> Path:
    user = getpass.getuser()
    cand = Path(f"/u/{user}/p4_ws/projects/ucie")
    return cand


def _windows_candidate() -> Path:
    user = getpass.getuser()
    for pattern in _WINDOWS_DEFAULTS:
        cand = Path(pattern.format(user=user)).expanduser().resolve()
        if cand.exists():
            return cand
    # Fall back to the primary expected layout even when not created yet.
    return Path(_WINDOWS_DEFAULTS[0].format(user=user)).expanduser().resolve()

def _scan_upwards_for_ucie(start: Path) -> Path | None:
    for p in start.resolve().parents:
        if p.name == 'ucie' and p.parent.name == 'projects':
            return p
    return None

def _resolve_projects_base() -> Path:
    env_val = os.environ.get("PROJECTS_ROOT")
    if env_val:
        return Path(env_val).expanduser().resolve()

    plat = os.name  # 'nt' or 'posix'
    if plat == 'nt':  # Windows
        return _windows_candidate()

    cand = _linux_candidate()
    if cand.exists():
        return cand.resolve()

    scanned = _scan_upwards_for_ucie(Path(__file__))
    if scanned and scanned.exists():
        return scanned.resolve()

    return Path.cwd().resolve()

PROJECTS_BASE: Path = _resolve_projects_base()

__all__ = ["PROJECTS_BASE"]
