"""Library counting use-cases (Phase 9)

Encapsulate recursive *.lib counting for Postedit_libs and PostQA_libs.
Routers become thin and depend only on these application classes.

Edge cases handled:
 - Missing target directory -> lib_count=0 + note message.
 - Non-directory path -> lib_count=0 + note.
 - Partial vs complete (complete when 16 libs found).
 - Errors during traversal -> captured in note (best-effort continue).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.infrastructure.fs import project_root


@dataclass
class CountPosteditLibsInput:
    project: str
    subproject: str
    cell: str
    postedit_libs_path: Optional[str] = None  # Custom path to Postedit_libs folder (overrides default)
    pvt_count: int = 8  # Number of PVT corners for this cell (default 8, expected libs = 2 * pvt_count)


@dataclass
class CountPosteditLibsOutput:
    project: str
    subproject: str
    cell: str
    path: str
    lib_count: int
    complete: bool
    expected_count: int  # 2 * pvt_count
    note: Optional[str]


class CountPosteditLibs:
    def execute(self, inp: CountPosteditLibsInput) -> CountPosteditLibsOutput:
        # Determine target path: use custom path if provided, otherwise default
        if inp.postedit_libs_path:
            target = Path(inp.postedit_libs_path) / inp.cell
        else:
            base = project_root.PROJECTS_BASE
            target = base / inp.project / inp.subproject / "design" / "timing" / "release" / "Postedit_libs" / inp.cell
        
        # Calculate expected lib count: 2 libs per PVT corner
        expected_count = 2 * inp.pvt_count
        
        note = None
        lib_count = 0
        if not target.exists():
            note = f"Postedit_libs folder does not exist: {target}"
        elif not target.is_dir():
            note = f"Postedit_libs path exists but is not a directory: {target}"
        else:
            try:
                lib_files = list(target.rglob("*.lib"))
                lib_count = len(lib_files)
                if lib_count == 0:
                    note = "No .lib files found in Postedit_libs folder"
                elif lib_count >= expected_count:
                    note = f"Found {lib_count} .lib files (complete, expected {expected_count})"
                else:
                    note = f"Found {lib_count} .lib files (expected {expected_count})"
            except Exception as e:
                note = f"Error counting .lib files: {e}"
        
        return CountPosteditLibsOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            path=str(target),
            lib_count=lib_count,
            complete=(lib_count >= expected_count),
            expected_count=expected_count,
            note=note,
        )


@dataclass
class CountPostqaLibsInput:
    project: str
    subproject: str
    cell: str
    pvt_count: int = 8  # Number of PVT corners for this cell (default 8, expected libs = 2 * pvt_count)


@dataclass
class CountPostqaLibsOutput:
    project: str
    subproject: str
    cell: str
    path: str
    lib_count: int
    complete: bool
    expected_count: int  # 2 * pvt_count
    note: Optional[str]


class CountPostqaLibs:
    def execute(self, inp: CountPostqaLibsInput) -> CountPostqaLibsOutput:
        base = project_root.PROJECTS_BASE
        target = base / inp.project / inp.subproject / "design" / "timing" / "release" / "PostQA_libs" / inp.cell
        
        # Calculate expected lib count: 2 libs per PVT corner (same as Postedit)
        expected_count = 2 * inp.pvt_count
        
        note = None
        lib_count = 0
        if not target.exists():
            note = f"PostQA_libs folder does not exist: {target}"
        elif not target.is_dir():
            note = f"PostQA_libs path exists but is not a directory: {target}"
        else:
            try:
                lib_files = list(target.rglob("*.lib"))
                lib_count = len(lib_files)
                if lib_count == 0:
                    note = "No .lib files found in PostQA_libs folder"
                elif lib_count >= expected_count:
                    note = f"Found {lib_count} .lib files (complete, expected {expected_count})"
                else:
                    note = f"Found {lib_count} .lib files (expected {expected_count})"
            except Exception as e:
                note = f"Error counting .lib files: {e}"
        return CountPostqaLibsOutput(
            project=inp.project,
            subproject=inp.subproject,
            cell=inp.cell,
            path=str(target),
            lib_count=lib_count,
            complete=(lib_count >= expected_count),
            expected_count=expected_count,
            note=note,
        )


__all__ = [
    "CountPosteditLibs", "CountPosteditLibsInput", "CountPosteditLibsOutput",
    "CountPostqaLibs", "CountPostqaLibsInput", "CountPostqaLibsOutput",
]
