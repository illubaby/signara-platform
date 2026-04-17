"""Filesystem-backed implementation of QCTablesRepository."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional
from app.domain.qc.entities import TableRowData
from app.domain.qc.repositories import QCTablesRepository
from .csv_loader import load_csv_rows, safe_float

class TablesRepositoryFS(QCTablesRepository):
    MAX_FILES = 50

    def build_tables(self, timing_paths: Optional[str], data: Optional[str]) -> Dict[str, List[TableRowData]]:
        delay: List[TableRowData] = []
        constraint: List[TableRowData] = []
        sources: List[Path] = []
        if timing_paths and Path(timing_paths).exists():
            sources.extend(Path(timing_paths).glob("*.csv"))
        elif data and Path(data).exists():
            sources.extend(Path(data).glob("*.csv"))
        for src in sources[: self.MAX_FILES]:
            rows = load_csv_rows(src)
            for r in rows:
                mode = (r.get("Mode") or r.get("Type") or "").lower()
                tb = r.get("Testbench") or r.get("TB") or src.stem
                pvt = r.get("PVT") or r.get("pvt") or "?"
                row = TableRowData(
                    testbench=tb,
                    pvt=pvt,
                    status=r.get("Status") or r.get("Result") or "Unknown",
                    slack=safe_float(r.get("Slack") or r.get("Slack(ns)")),
                    factorx=safe_float(r.get("FactorX") or r.get("FX")),
                    program_time=r.get("ProgramTime") or r.get("Runtime"),
                    path=str(src),
                )
                if "constraint" in mode:
                    constraint.append(row)
                else:
                    delay.append(row)
        return {"delay": delay, "constraint": constraint}
