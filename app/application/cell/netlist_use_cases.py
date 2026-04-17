from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List
import re

from app.infrastructure.fs.project_root import PROJECTS_BASE


@dataclass
class IntNetlistVersionInput:
    project: str
    subproject: str
    cell: str


@dataclass
class IntNetlistVersionOutput:
    cell: str
    netlist_version: str
    base_extr_dir: str
    target_dir: str
    target_exists: bool


class IntNetlistVersion:
    """Compute INT netlist version for NT cells (snapHier) using SAF's logic."""
    def execute(self, inp: IntNetlistVersionInput) -> IntNetlistVersionOutput:
        base_root = PROJECTS_BASE
        extr_cell_dir = base_root / inp.project / inp.subproject / "design" / "timing" / "extr" / inp.cell
        if not extr_cell_dir.exists():
            return IntNetlistVersionOutput(
                cell=inp.cell,
                netlist_version="Missing",
                base_extr_dir=str(extr_cell_dir),
                target_dir=str(extr_cell_dir / "nt" / "int"),
                target_exists=False,
            )

        target_dir = extr_cell_dir / "nt" / "int"
        netlist_files: List[Path] = []
        try:
            patterns = [f"{inp.cell}.sp", f"{inp.cell}.spf", f"{inp.cell}_*.sp", f"{inp.cell}_*.spf"]
            if target_dir.exists():
                for patt in patterns:
                    netlist_files.extend(list(target_dir.glob(patt)))
        except Exception:
            netlist_files = []

        if not netlist_files:
            try:
                if extr_cell_dir.exists():
                    for p in extr_cell_dir.iterdir():
                        if p.is_file() and p.suffix in (".sp", ".spf"):
                            name = p.name
                            if name == f"{inp.cell}.sp" or name == f"{inp.cell}.spf" or name.startswith(f"{inp.cell}_"):
                                netlist_files.append(p)
            except Exception:
                netlist_files = []

        if not netlist_files:
            return IntNetlistVersionOutput(
                cell=inp.cell,
                netlist_version="Missing",
                base_extr_dir=str(extr_cell_dir),
                target_dir=str(target_dir),
                target_exists=target_dir.exists(),
            )

        file_versions: dict[str, int] = {}
        for nf in netlist_files:
            try:
                with nf.open("r", errors="ignore") as f:
                    for line in f:
                        if "snapHier.txt" in line and "#" in line:
                            matches = re.findall(r"#(\d+)", line)
                            if matches:
                                file_versions[nf.name] = int(matches[0])
                                break
            except Exception:
                continue

        if not file_versions:
            return IntNetlistVersionOutput(
                cell=inp.cell,
                netlist_version="nolpe",
                base_extr_dir=str(extr_cell_dir),
                target_dir=str(target_dir),
                target_exists=target_dir.exists(),
            )

        unique = set(file_versions.values())
        if len(unique) > 1:
            min_ver = min(unique); max_ver = max(unique)
            min_adj = min_ver - 1 if min_ver > 0 else min_ver
            max_adj = max_ver - 1 if max_ver > 0 else max_ver
            return IntNetlistVersionOutput(
                cell=inp.cell,
                netlist_version=f"Mismatch: #{min_adj}-#{max_adj}",
                base_extr_dir=str(extr_cell_dir),
                target_dir=str(target_dir),
                target_exists=target_dir.exists(),
            )

        version = next(iter(unique))
        adj = version - 1 if version > 0 else version
        return IntNetlistVersionOutput(
            cell=inp.cell,
            netlist_version=f"#{adj}",
            base_extr_dir=str(extr_cell_dir),
            target_dir=str(target_dir),
            target_exists=target_dir.exists(),
        )
