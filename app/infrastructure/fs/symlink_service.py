"""Shared symlink service for creating platform-appropriate links.

This is a generic, reusable service for creating symlinks across all features
(QC, SAF, QA, etc.). Follows the simple principle:
- If file/folder exists (symlink or real) → skip it
- If file/folder doesn't exist → create symlink

Windows fallback: attempts symlink first, copies on failure.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional
import shutil
import os


@dataclass
class SymlinkResult:
    """Result of symlink operations with detailed status."""
    note: str
    warnings: List[str]
    results: List[str]
    meta: Dict[str, str]


class SymlinkService:
    """Generic symlink service for cross-platform link creation."""
    
    def __init__(self, startup_dir: Optional[Path] = None):
        """Initialize with startup directory (defaults to bin/python/)."""
        if startup_dir is None:
            app_dir = Path(__file__).parent.parent.parent  # app/infrastructure/fs/ -> app/
            startup_dir = app_dir.parent  # bin/python/
        self.startup_dir = startup_dir

    def link_cell_tools(self, cell_root: Path) -> SymlinkResult:
        """Create symlinks for TimingCloseBeta.py and bin/ in cell directory.
        
        Simple logic:
        - If target exists (symlink or real) → skip
        - If target doesn't exist → create symlink
        
        Args:
            cell_root: Target directory where links will be created
            
        Returns:
            SymlinkResult with status of operations
        """
        timing_src = self.startup_dir / "TimingCloseBeta.py"
        bin_src = self.startup_dir / "bin"
        timing_link = cell_root / "TimingCloseBeta.py"
        bin_link = cell_root / "bin"
        
        results: List[str] = []
        warnings: List[str] = []
        meta: Dict[str, str] = {}

        # Ensure cell_root exists so link operations don't fail on missing directory
        if not cell_root.exists():
            try:
                cell_root.mkdir(parents=True, exist_ok=True)
                results.append(f"✓ Created cell_root directory: {cell_root}")
                meta["cell_root_create"] = "created"
            except Exception as e:
                warnings.append(f"✗ Failed to create cell_root directory {cell_root}: {e}")
                meta["cell_root_create"] = "failed"
        else:
            meta["cell_root_create"] = "exists"
        
        # Handle TimingCloseBeta.py
        if timing_src.exists():
            if timing_link.exists():
                results.append("TimingCloseBeta.py already exists; skipped")
                meta["timing_status"] = "exists"
            else:
                try:
                    timing_link.symlink_to(timing_src)
                    results.append(f"✓ Linked TimingCloseBeta.py -> {timing_src}")
                    meta["timing_status"] = "linked"
                except OSError as e:
                    # Fallback to copy on Windows or permission issues
                    try:
                        shutil.copy2(timing_src, timing_link)
                        warnings.append(f"⚠ Copied TimingCloseBeta.py (symlink failed: {e})")
                        meta["timing_status"] = "copied"
                    except Exception as copy_err:
                        warnings.append(f"✗ Failed TimingCloseBeta.py: {copy_err}")
                        meta["timing_status"] = "failed"
        else:
            warnings.append(f"✗ Source not found: {timing_src}")
            meta["timing_status"] = "source_missing"
        
        # Handle bin/ directory
        if bin_src.exists() and bin_src.is_dir():
            if bin_link.exists():
                results.append("bin/ already exists; skipped")
                meta["bin_status"] = "exists"
            else:
                try:
                    bin_link.symlink_to(bin_src, target_is_directory=True)
                    results.append(f"✓ Linked bin/ -> {bin_src}")
                    meta["bin_status"] = "linked"
                except OSError as e:
                    # Windows may need junction or copy fallback
                    if os.name == 'nt':
                        try:
                            import subprocess as _sp
                            _sp.run(
                                ["cmd", "/c", "mklink", "/D", str(bin_link), str(bin_src)],
                                check=True,
                                capture_output=True
                            )
                            results.append(f"✓ Created bin/ junction (Windows) -> {bin_src}")
                            meta["bin_status"] = "junction"
                        except Exception as mk_err:
                            warnings.append(f"⚠ Symlink/junction failed for bin/ (error: {e})")
                            meta["bin_status"] = "failed"
                    else:
                        warnings.append(f"✗ Failed bin/ link: {e}")
                        meta["bin_status"] = "failed"
        else:
            warnings.append(f"✗ Source not found: {bin_src}")
            meta["bin_status"] = "source_missing"
        
        meta["startup_dir"] = str(self.startup_dir)
        meta["cell_root"] = str(cell_root)
        
        note = " | ".join(results + warnings) if (results or warnings) else "No symlinks created"
        return SymlinkResult(note=note, warnings=warnings, results=results, meta=meta)
    
    # ------------------------------------------------------------------
    # Compatibility shim
    # SAF use case EnsureSafSymlinks (Phase 2 migration) still calls
    # service.create_platform_links(cell_root). That method originally
    # lived on SafSymlinkService. We expose it here to avoid runtime
    # AttributeError and delegate to the canonical implementation.
    # ------------------------------------------------------------------
    def create_platform_links(self, cell_root: Path) -> SymlinkResult:  # pragma: no cover (thin wrapper)
        return self.link_cell_tools(cell_root)
    
    def link_directory(
        self,
        source: Path,
        target: Path,
        name: str = "directory"
    ) -> Dict[str, Optional[str]]:
        """Generic method to link any directory.
        
        Args:
            source: Source directory to link from
            target: Target path where symlink will be created
            name: Human-readable name for logging
            
        Returns:
            Dict with 'created' (bool), 'note' (str), 'error' (str or None)
        """
        results: List[str] = []
        
        # Check if target already exists
        if target.exists():
            if target.is_symlink():
                try:
                    current_target = target.resolve()
                    if current_target == source.resolve():
                        return {
                            "created": False,
                            "note": f"✓ {name} symlink already exists and points to correct target",
                            "error": None
                        }
                    else:
                        return {
                            "created": False,
                            "note": f"⚠ {name} symlink exists but points to different target: {current_target}",
                            "error": None
                        }
                except Exception as e:
                    return {
                        "created": False,
                        "note": f"⚠ Cannot resolve {name} symlink: {e}",
                        "error": str(e)
                    }
            else:
                return {
                    "created": False,
                    "note": f"✓ {name} directory already exists (real directory)",
                    "error": None
                }
        
        # Check if source exists
        if not source.exists():
            return {
                "created": False,
                "note": f"✗ Source {name} not found: {source}",
                "error": f"Source directory not found: {source}"
            }
        
        # Create symlink
        results.append(f"Creating {name} symlink -> {source}")
        try:
            target.symlink_to(source, target_is_directory=True)
            results.append(f"✓ Successfully created {name} symlink")
            return {"created": True, "note": " | ".join(results), "error": None}
        except OSError as e:
            # Try Windows junction as fallback
            if os.name == 'nt':
                try:
                    import subprocess as _sp
                    _sp.run(
                        ["cmd", "/c", "mklink", "/D", str(target), str(source)],
                        check=True,
                        capture_output=True
                    )
                    results.append(f"✓ Created {name} junction (Windows)")
                    return {"created": True, "note": " | ".join(results), "error": None}
                except Exception as mk_err:
                    results.append(f"✗ Failed to create symlink/junction: {mk_err}")
                    return {
                        "created": False,
                        "note": " | ".join(results),
                        "error": f"Symlink failed: {e}, mklink failed: {mk_err}"
                    }
            else:
                results.append(f"✗ Failed to create symlink: {e}")
                return {
                    "created": False,
                    "note": " | ".join(results),
                    "error": f"Symlink creation failed: {e}"
                }
        except Exception as e:
            results.append(f"✗ Unexpected error creating symlink: {e}")
            return {"created": False, "note": " | ".join(results), "error": str(e)}

    def ensure_nt_share_link(self, project: str, subproject: str, nt_root: Path) -> Dict[str, Optional[str]]:
        """Create NT share symlink for SAF feature.
        
        Links nt_root/share to /remote/cad-rep/projects/ucie/{project}/{subproject}/design/timing/nt/share
        
        Args:
            project: Project name
            subproject: Subproject name
            nt_root: NT root directory where share/ symlink will be created
            
        Returns:
            Dict with 'created' (bool), 'note' (str), 'error' (str or None)
        """
        share_link = nt_root / "share"
        share_target = Path(f"/remote/cad-rep/projects/ucie/{project}/{subproject}/design/timing/nt/share")
        results: List[str] = []
        
        # If exists as real directory, leave it alone
        if share_link.exists() and not share_link.is_symlink():
            return {"created": False, "note": f"✓ share/ directory already exists at {share_link}", "error": None}
        
        # If symlink exists, check if it points to correct target
        if share_link.is_symlink():
            try:
                current_target = share_link.resolve()
                if current_target == share_target.resolve():
                    return {"created": False, "note": "✓ share/ symlink already exists and points to correct target", "error": None}
                else:
                    results.append(f"⚠ share/ symlink points to wrong target: {current_target}")
                    results.append("🔄 Removing old symlink and recreating")
                    try:
                        share_link.unlink()
                    except Exception as e:
                        return {"created": False, "note": " | ".join(results), "error": f"Failed to remove old symlink: {e}"}
            except Exception as e:
                results.append(f"⚠ Cannot resolve symlink target: {e}")
        
        # Check if target exists
        if not share_target.exists():
            return {"created": False, "note": f"✗ Target share folder does not exist: {share_target}", "error": f"Target directory not found: {share_target}"}
        
        # Create symlink
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


__all__ = ["SymlinkService", "SymlinkResult"]
