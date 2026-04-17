"""Version check API router."""
import os
import sys
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

import re

from app.application.version import CheckVersion
from app.infrastructure.p4.version_repository_p4 import VersionRepositoryP4
from app.infrastructure.logging.logging_config import get_logger
from app import __version__

router = APIRouter(tags=["version"])
logger = get_logger(__name__)

# Path to CHANGELOG.md in changelog folder
CHANGELOG_PATH = Path(__file__).parent.parent.parent.parent / "changelog" / "CHANGELOG.md"


class VersionResponse(BaseModel):
    """Version check response schema."""
    local_version: str
    remote_version: Optional[str]
    deadline: Optional[str]  # ISO format string
    is_outdated: bool
    is_past_deadline: bool
    must_update: bool
    remote_changelog: Optional[str] = None  # Changelog for the remote version


class UpdateResponse(BaseModel):
    """Update trigger response schema."""
    success: bool
    message: str


@router.get("/api/version/check", response_model=VersionResponse)
async def check_version():
    """Check application version against remote P4 depot.
    
    Returns version comparison info including:
    - local_version: Current running version
    - remote_version: Latest version in P4 depot (None if fetch failed)
    - deadline: Mandatory update deadline (None if not set)
    - is_outdated: True if local != remote
    - is_past_deadline: True if current time > deadline
    - must_update: True if outdated AND past deadline (blocks usage)
    - remote_changelog: Changelog content for the remote version (if outdated)
    """
    from app import __version_depot_path__
    
    repo = VersionRepositoryP4()
    use_case = CheckVersion(repo)
    info = use_case.execute()
    
    # Fetch remote changelog only if outdated (to show what's new in the update)
    remote_changelog = None
    if info.is_outdated and info.remote_version:
        remote_changelog = repo.get_remote_changelog(__version_depot_path__, info.remote_version)
    
    return VersionResponse(
        local_version=info.local_version,
        remote_version=info.remote_version,
        deadline=info.deadline.isoformat() if info.deadline else None,
        is_outdated=info.is_outdated,
        is_past_deadline=info.is_past_deadline,
        must_update=info.must_update,
        remote_changelog=remote_changelog
    )


@router.post("/api/version/update", response_model=UpdateResponse)
async def trigger_update():
    """Trigger application update by replacing the current process.
    
    This endpoint will:
    1. Return a success response to the client
    2. Replace the current Python process with: TimingCloseBeta.py -update -web
    
    Note: The response is sent before the process replacement, so the client
    should expect the connection to close shortly after.
    """
    import threading
    
    def do_update():
        """Execute update in a separate thread after a brief delay."""
        import time
        time.sleep(0.5)  # Give time for response to be sent
        
        logger.info("[trigger_update] Replacing current process with update command...")
        logger.info(f"[trigger_update] Current working directory: {os.getcwd()}")
        
        update_script = "./TimingCloseBeta.py"
        update_args = ["TimingCloseBeta.py", "-update", "-web"]
        
        logger.info(f"[trigger_update] Executing: {' '.join(update_args)}")
        
        try:
            os.execv(update_script, update_args)
        except Exception as ex:
            logger.error(f"[trigger_update] Failed to exec: {ex}")
    
    # Start update in background thread
    update_thread = threading.Thread(target=do_update, daemon=True)
    update_thread.start()
    
    logger.info("[trigger_update] Update scheduled, returning response...")
    return UpdateResponse(
        success=True,
        message="Update initiated. The application will restart shortly."
    )


@router.get("/api/version/changelog", response_class=PlainTextResponse)
async def get_changelog():
    """Get the full changelog content.
    
    Returns the entire CHANGELOG.md file for display when
    clicking the version badge.
    """
    logger.info(f"[get_changelog] Looking for CHANGELOG.md at {CHANGELOG_PATH}")
    try:
        if CHANGELOG_PATH.exists():
            content = CHANGELOG_PATH.read_text(encoding="utf-8")
            logger.info(f"[get_changelog] Found changelog, {len(content)} bytes")
            return content
        else:
            logger.warning(f"[get_changelog] CHANGELOG.md not found at {CHANGELOG_PATH}")
            return "# Changelog\n\nNo changelog available."
    except Exception as ex:
        logger.error(f"[get_changelog] Failed to read changelog: {ex}")
        return "# Changelog\n\nFailed to load changelog."


def extract_version_section(content: str, version: str) -> str | None:
    """Extract the changelog section for a specific version.
    
    Looks for ## v{version} and returns everything until the next ## or ---
    """
    # Pattern to match version header (## v1.0.0 or ## 1.0.0)
    pattern = rf"(## v?{re.escape(version)}.*?)(?=\n## |\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None
