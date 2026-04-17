"""SAF symlink service (Phase 9) - Migrated to use shared SymlinkService

Provides creation of platform-appropriate links for TimingCloseBeta.py,
bin/, and NT share directory. Now delegates to the shared SymlinkService
for cell tools and provides SAF-specific NT share linking.

Windows fallback: attempts mklink for directory junction, else copies.
All operations best-effort and return structured metadata.
"""
from __future__ import annotations

from pathlib import Path
import os
from typing import List, Dict, Optional

# Import shared symlink service and result type
from app.infrastructure.fs.symlink_service import SymlinkService, SymlinkResult


class SafSymlinkService:
    """SAF-specific symlink service with NT share support."""
    
    def __init__(self, startup_dir: Optional[Path] = None):
        """Initialize with startup directory (defaults to bin/python/)."""
        # Delegate to shared SymlinkService for cell tools
        self._symlink_service = SymlinkService(startup_dir)
        self.startup_dir = self._symlink_service.startup_dir

    def create_platform_links(self, cell_root: Path) -> SymlinkResult:
        """Create symlinks for TimingCloseBeta.py and bin/ in cell directory.
        
        Delegates to the shared SymlinkService.link_cell_tools() method.
        
        Args:
            cell_root: Target directory where links will be created
            
        Returns:
            SymlinkResult with status of operations
        """
        return self._symlink_service.link_cell_tools(cell_root)

    def ensure_nt_share_link(self, project: str, subproject: str, nt_root: Path) -> Dict[str, Optional[str]]:
        share_link = nt_root / "share"
        share_target = Path(f"/remote/cad-rep/projects/ucie/{project}/{subproject}/design/timing/nt/share")
        results: List[str] = []
        if share_link.exists() and not share_link.is_symlink():
            return {"created": False, "note": f"✓ share/ directory already exists at {share_link}", "error": None}
        if share_link.is_symlink():
            try:
                current_target = share_link.resolve()
                if current_target == share_target.resolve():
                    return {"created": False, "note": "✓ share/ symlink already exists and points to correct target", "error": None}
                else:
                    results.append(f"⚠ share/ symlink points to wrong target: {current_target}")
                    results.append("🔄 Removing old symlink and recreating")
                    try: share_link.unlink()
                    except Exception as e:
                        return {"created": False, "note": " | ".join(results), "error": f"Failed to remove old symlink: {e}"}
            except Exception as e:
                results.append(f"⚠ Cannot resolve symlink target: {e}")
        if not share_target.exists():
            return {"created": False, "note": f"✗ Target share folder does not exist: {share_target}", "error": f"Target directory not found: {share_target}"}
        results.append(f"🔄 Creating share/ symlink -> {share_target}")
        try:
            share_link.symlink_to(share_target, target_is_directory=True)
            results.append("✓ Successfully created share/ symlink")
            return {"created": True, "note": " | ".join(results), "error": None}
        except OSError as e:
            if os.name == 'nt':
                try:
                    import subprocess as _sp
                    _sp.run(["cmd", "/c", "mklink", "/D", str(share_link), str(share_target)], check=True, capture_output=True)
                    results.append("✓ Created share/ junction (Windows)")
                    return {"created": True, "note": " | ".join(results), "error": None}
                except Exception as mk_err:
                    results.append(f"✗ Failed to create symlink/junction: {mk_err}")
                    return {"created": False, "note": " | ".join(results), "error": f"Symlink failed: {e}, mklink failed: {mk_err}"}
            else:
                results.append(f"✗ Failed to create symlink: {e}")
                return {"created": False, "note": " | ".join(results), "error": f"Symlink creation failed: {e}"}
        except Exception as e:
            results.append(f"✗ Unexpected error creating symlink: {e}")
            return {"created": False, "note": " | ".join(results), "error": str(e)}


__all__ = ["SafSymlinkService", "SymlinkResult"]
