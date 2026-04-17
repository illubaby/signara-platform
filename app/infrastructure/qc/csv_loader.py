"""CSV loading utilities for QC tables (pure IO + parsing)."""
from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Optional
import csv

def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    try:
        with path.open(newline="", encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append({k.strip(): (v.strip() if isinstance(v, str) else v) for k, v in r.items()})
    except Exception:
        return []
    return rows


def safe_float(v) -> Optional[float]:
    if v is None:
        return None
    try:
        return float(str(v).strip())
    except Exception:
        return None
