"""Symlink orchestration use-case for SAF cells.

Delegates platform link creation to the shared ``SymlinkService``. A legacy
``SafSymlinkService`` wrapper has been removed; ``SymlinkService`` now exposes
``create_platform_links`` (shim to ``link_cell_tools``) for backward
compatibility. This use case should remain thin and never perform direct
filesystem operations beyond invoking the service and simple conditional logic
for SAF-specific links (common_source for SiS, share/ for NT).
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
import os

from app.infrastructure.fs.symlink_service import SymlinkService

@dataclass
class EnsureSafSymlinksInput:
    project: str
    subproject: str
    cell_root: Path  # root path of sis/nt timing cell (not the cell subfolder if design requires root-level links)
    cell_dir: Path   # actual cell directory
    cell_type: str   # 'sis' or 'nt'

@dataclass
class EnsureSafSymlinksOutput:
    notes: List[str]
    warnings: List[str]

class EnsureSafSymlinks:
    def __init__(self, service: Optional[SymlinkService] = None):
        self.service = service or SymlinkService()

    def execute(self, inp: EnsureSafSymlinksInput) -> EnsureSafSymlinksOutput:
        notes: List[str] = []
        warnings: List[str] = []
        # platform links (TimingCloseBeta.py, bin folder)
        try:
            res = self.service.create_platform_links(inp.cell_root)
            notes.append(res.note)
            warnings.extend(res.warnings)
        except Exception as e:
            warnings.append(f"platform links exception: {e}")
        # common_source (SiS only)
        if inp.cell_type == 'sis':
            try:
                target = Path(f"/remote/cad-rep/projects/ucie/{inp.project}/{inp.subproject}/design/timing/sis/common_source")
                link_path = inp.cell_root / "common_source"
                if not link_path.exists():
                    if link_path.is_symlink() or link_path.exists():
                        try: link_path.unlink()
                        except Exception: pass
                    try:
                        os.symlink(target, link_path, target_is_directory=True)
                        notes.append("Linked common_source")
                    except FileExistsError:
                        pass
                    except OSError as e:
                        if os.name == 'nt':
                            try:
                                import subprocess as _sp
                                _sp.run(["cmd", "/c", "mklink", "/J", str(link_path), str(target)], check=False)
                                notes.append("Created common_source junction (Windows)")
                            except Exception:
                                warnings.append(f"common_source link failed: {e}")
                        else:
                            warnings.append(f"common_source link failed: {e}")
                else:
                    notes.append("common_source exists")
            except Exception as e:
                warnings.append(f"common_source setup exception: {e}")
        # NT share link (NT only)
        if inp.cell_type == 'nt':
            try:
                share_result = self.service.ensure_nt_share_link(inp.project, inp.subproject, inp.cell_root)
                notes.append(share_result.get('note', 'NT share handled'))
                if share_result.get('error'):
                    warnings.append(share_result['error'])
            except Exception as e:
                warnings.append(f"nt share setup exception: {e}")
        return EnsureSafSymlinksOutput(notes=notes, warnings=warnings)

__all__ = ["EnsureSafSymlinks", "EnsureSafSymlinksInput", "EnsureSafSymlinksOutput"]
