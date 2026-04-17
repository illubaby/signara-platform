from __future__ import annotations

from typing import Protocol


class ScriptRepository(Protocol):
    """Port for persisting generated script files."""
    def write_script(self, filename: str, content: str, output_dir: str | None = None) -> None: ...
