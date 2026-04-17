"""Infrastructure adapter for reading Excel workbooks.

Implements the ExcelReaderPort using pandas when available. Falls back
to error-only sheets if pandas or openpyxl is missing.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict

from app.application.explorer.ports import ExcelReaderPort
from app.domain.explorer.models import ExcelWorkbook, ExcelSheet

class PandasExcelReader(ExcelReaderPort):
    def __init__(self, max_rows_per_sheet: int = 1000):
        self.max_rows_per_sheet = max_rows_per_sheet

    def read_workbook(self, path: Path, max_rows: int | None = None) -> ExcelWorkbook:
        limit = max_rows or self.max_rows_per_sheet
        try:
            import pandas as pd  # type: ignore
        except Exception:
            # Return a workbook structure indicating missing dependency
            sheet = ExcelSheet(
                name="error",
                columns=["message"],
                rows=[["pandas or engine not installed"]],
                row_count=1,
                truncated=False,
                error="pandas library not installed. Install pandas & openpyxl"
            )
            return ExcelWorkbook(sheets={"error": sheet}, sheet_names=["error"], truncated=False)

        try:
            xl = pd.ExcelFile(path)
        except Exception as e:
            sheet = ExcelSheet(
                name="error",
                columns=["message"],
                rows=[[f"Failed to open workbook: {e}"]],
                row_count=1,
                truncated=False,
                error=str(e)
            )
            return ExcelWorkbook(sheets={"error": sheet}, sheet_names=["error"], truncated=False)

        sheets: Dict[str, ExcelSheet] = {}
        truncated_any = False
        for sheet_name in xl.sheet_names:
            try:
                df = pd.read_excel(xl, sheet_name=sheet_name, nrows=limit + 1)
                truncated = False
                if len(df) > limit:
                    df = df.head(limit)
                    truncated = True
                    truncated_any = True
                sheets[sheet_name] = ExcelSheet(
                    name=sheet_name,
                    columns=df.columns.tolist(),
                    rows=df.fillna('').values.tolist(),
                    row_count=len(df),
                    truncated=truncated,
                    error=None
                )
            except Exception as e:
                sheets[sheet_name] = ExcelSheet(
                    name=sheet_name,
                    columns=["error"],
                    rows=[[str(e)]],
                    row_count=1,
                    truncated=False,
                    error=str(e)
                )
        return ExcelWorkbook(sheets=sheets, sheet_names=xl.sheet_names, truncated=truncated_any)

__all__ = ["PandasExcelReader"]