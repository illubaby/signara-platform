from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class SyncIntNetlistInput:
    project: str
    subproject: str
    cell: str


@dataclass
class SyncIntNetlistOutput:
    project: str
    subproject: str
    cell: str
    depot_path: str
    synced: bool
    return_code: int
    stdout: str
    stderr: str
    note: Optional[str] = None


class SyncIntNetlist:
    """Force-sync INT netlist from the extraction depot path.

    Uses a simple subprocess call to `p4 sync -f` on the NT extraction path.
    Kept minimal per request; error strings are truncated.
    """

    def execute(self, inp: SyncIntNetlistInput) -> SyncIntNetlistOutput:
        depot_path = f"//wwcad/msip/projects/ucie/{inp.project}/{inp.subproject}/design/timing/extr/{inp.cell}/nt/..."
        import subprocess
        try:
            proc = subprocess.run(["p4", "sync", "-f", depot_path], capture_output=True, text=True, timeout=300)
            ok = proc.returncode == 0
            note = (f"Synced INT netlist" if ok else f"P4 sync failed ({proc.returncode})")
            return SyncIntNetlistOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell=inp.cell,
                depot_path=depot_path,
                synced=ok,
                return_code=proc.returncode,
                stdout=(proc.stdout or "")[:10000],
                stderr=(proc.stderr or "")[:8000],
                note=note,
            )
        except subprocess.TimeoutExpired:
            return SyncIntNetlistOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell=inp.cell,
                depot_path=depot_path,
                synced=False,
                return_code=-1,
                stdout="",
                stderr="Timeout",
                note="Timeout (300s)",
            )
        except FileNotFoundError:
            return SyncIntNetlistOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell=inp.cell,
                depot_path=depot_path,
                synced=False,
                return_code=-1,
                stdout="",
                stderr="p4 not found",
                note="Perforce client not installed",
            )
        except Exception as e:
            return SyncIntNetlistOutput(
                project=inp.project,
                subproject=inp.subproject,
                cell=inp.cell,
                depot_path=depot_path,
                synced=False,
                return_code=-1,
                stdout="",
                stderr=str(e),
                note=f"Unexpected error: {e}",
            )
