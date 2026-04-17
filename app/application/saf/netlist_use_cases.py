"""Netlist-related SAF application use-cases (Phase 7).

SyncNetlist: force-sync extraction netlist files from Perforce depot path.
GetNetlistDebug: gather diagnostic info about netlist presence & versions.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict
import re

from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.infrastructure.fs.saf_cell_repository_fs import SafCellRepositoryFS
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4


@dataclass
class SyncNetlistInput:
    project: str
    subproject: str
    cell: str
    cell_type: str  # 'sis' or 'nt'

@dataclass
class SyncNetlistOutput:
    depot_path: str
    synced: bool
    return_code: int
    stdout: str
    stderr: str
    file_count: int
    note: str


class SyncNetlist:
    def __init__(self, p4_repo: SafPerforceRepositoryP4):
        self._p4 = p4_repo

    def execute(self, inp: SyncNetlistInput) -> SyncNetlistOutput:
        if inp.cell_type == 'nt':
            depot_path = f"//wwcad/msip/projects/ucie/{inp.project}/{inp.subproject}/design/timing/extr/{inp.cell}/nt/etm/..."
        else:
            depot_path = f"//wwcad/msip/projects/ucie/{inp.project}/{inp.subproject}/design/timing/extr/{inp.cell}/sis/..."
        # Use generic sync via subprocess (repository method could be extended).
        import subprocess
        try:
            proc = subprocess.run(["p4", "sync", "-f", depot_path], capture_output=True, text=True, timeout=300)
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            sync_lines = [l for l in stdout.split('\n') if l.strip() and '#' in l]
            file_count = len(sync_lines)
            note = (
                f"Successfully synced {file_count} file(s)" if proc.returncode == 0 else f"P4 sync failed (code {proc.returncode})"
            )
            return SyncNetlistOutput(depot_path=depot_path, synced=proc.returncode == 0, return_code=proc.returncode, stdout=stdout[:10000], stderr=stderr[:10000], file_count=file_count, note=note)
        except subprocess.TimeoutExpired:
            return SyncNetlistOutput(depot_path=depot_path, synced=False, return_code=-1, stdout="", stderr="Timeout", file_count=0, note="Timeout (300s)")
        except FileNotFoundError:
            return SyncNetlistOutput(depot_path=depot_path, synced=False, return_code=-1, stdout="", stderr="p4 not found", file_count=0, note="Perforce client not installed")
        except Exception as e:
            return SyncNetlistOutput(depot_path=depot_path, synced=False, return_code=-1, stdout="", stderr=str(e), file_count=0, note=f"Unexpected error: {e}")


@dataclass
class GetNetlistDebugInput:
    project: str
    subproject: str
    cell: str
    cell_type: str  # 'sis' or 'nt'

@dataclass
class NetlistFileInfo:
    name: str
    version: str
    path: str

@dataclass
class GetNetlistDebugOutput:
    cell: str
    cell_type: str
    netlist_version: str
    base_extr_dir: str
    base_exists: bool
    target_dir: str
    target_exists: bool
    expected_pattern: str
    spf_files: List[NetlistFileInfo]
    fallback_search: bool


class GetNetlistDebug:
    def __init__(self, fs_repo: SafCellRepositoryFS):
        self._fs = fs_repo

    def execute(self, inp: GetNetlistDebugInput) -> GetNetlistDebugOutput:
        extr_cell_dir = PROJECTS_BASE / inp.project / inp.subproject / "design" / "timing" / "extr" / inp.cell
        base_exists = extr_cell_dir.exists()
        if inp.cell_type == 'nt':
            target_dir = extr_cell_dir / 'nt' / 'etm'
        else:
            target_dir = extr_cell_dir / 'sis'
        target_exists = target_dir.exists()
        expected_pattern = f"{inp.cell}.sp/.spf or {inp.cell}_*.sp/.spf"
        netlist_files: List[Path] = []
        fallback_search = False
        try:
            if target_exists:
                patterns = [f"{inp.cell}.sp", f"{inp.cell}.spf", f"{inp.cell}_*.sp", f"{inp.cell}_*.spf"]
                for patt in patterns:
                    netlist_files.extend(list(target_dir.glob(patt)))
            else:
                fallback_search = True
                if base_exists:
                    for p in extr_cell_dir.iterdir():
                        if p.is_file() and p.suffix in ('.sp', '.spf'):
                            if p.name == f"{inp.cell}.sp" or p.name == f"{inp.cell}.spf" or p.name.startswith(f"{inp.cell}_"):
                                netlist_files.append(p)
        except Exception:
            pass
        file_infos: List[NetlistFileInfo] = []
        for nf in netlist_files:
            version = "Not found"
            try:
                with nf.open('r', errors='ignore') as f:
                    for line in f:
                        if 'snapHier.txt' in line and '#' in line:
                            matches = re.findall(r"#(\d+)", line)
                            if matches:
                                raw_version = int(matches[0])
                                adj = raw_version - 1 if raw_version > 0 else raw_version
                                version = f"#{adj}"
                                break
            except Exception:
                version = "Error reading file"
            file_infos.append(NetlistFileInfo(name=nf.name, version=version, path=str(nf)))
        netlist_version = self._fs.netlist_version(inp.project, inp.subproject, inp.cell, inp.cell_type)
        return GetNetlistDebugOutput(
            cell=inp.cell,
            cell_type=inp.cell_type,
            netlist_version=netlist_version,
            base_extr_dir=str(extr_cell_dir),
            base_exists=base_exists,
            target_dir=str(target_dir),
            target_exists=target_exists,
            expected_pattern=expected_pattern,
            spf_files=file_infos,
            fallback_search=fallback_search,
        )
