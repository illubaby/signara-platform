from __future__ import annotations

import os
from pathlib import Path

from app.domain.script.repositories import ScriptRepository


class ScriptRepositoryFS(ScriptRepository):
    def __init__(self, base_dir: str | None = None):
        self.base_dir = Path(base_dir or os.getcwd())

    def write_script(self, filename: str, content: str, output_dir: str | None = None) -> None:  # type: ignore[override]
        """Write script to file.
        
        Args:
            filename: Name of the script file
            content: Content to write
            output_dir: Optional directory path. If provided, writes to this directory.
                       Otherwise, uses the base_dir from constructor.
        """
        target_dir = Path(output_dir) if output_dir else self.base_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / filename
        path.write_text(content, encoding="utf-8")
        # Make the script executable (chmod +x). This is primarily for POSIX environments.
        try:
            current_mode = path.stat().st_mode
            path.chmod(current_mode | 0o111)
        except Exception:
            # On some platforms (e.g., Windows), chmod may not behave as expected; ignore errors.
            pass
