from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.script.repositories import ScriptRepository


@dataclass(frozen=True)
class OptionPair:
    key: str
    value: str | None  # value can be empty for flags
    line_ending: str | None = None  # custom line ending (None = use default fill_space)
    no_prefix: bool = False  # if True, don't add '-' prefix (bare option)

    def to_lines(self) -> list[str]:
        if self.value is None or self.value == "":
            # Flag: -key or just key (if no_prefix)
            return [self.key] if self.no_prefix else [f"-{self.key}"]
        # Key-value: -key value or just key value (if no_prefix)
        return [f"{self.key} {self.value}"] if self.no_prefix else [f"-{self.key} {self.value}"]


class GenerateRunAllScript:
    """Use case: generate a runall.csh script with given command and options.
    fill_space is the separator inserted after each option line except the last.
    Default fill_space is ' \\' (space + backslash).
    """

    def __init__(self, repo: ScriptRepository):
        self.repo = repo

    def execute(
        self,
        command: str,
        options: Sequence[OptionPair],
        fill_space: str = " \\",
        command_line_ending: str | None = None,
        output_dir: str | None = None,
        script_name: str = "runall.csh",
    ) -> str:
        """Generate and save script file.
        
        Args:
            command: The command to execute
            options: List of command-line options
            fill_space: Line continuation separator (default: ' \\\\')
            command_line_ending: Custom line ending for command line (overrides fill_space)
            output_dir: Optional directory where script should be created.
                       If None, uses repository's default directory.
            script_name: Name of the script file (default: 'runall.csh')
        
        Returns:
            Generated script content
        """
        shebang = "#!/bin/csh -f"
        lines: list[str] = [shebang]

        if options:
            # Use custom command_line_ending if specified, otherwise use fill_space
            cmd_ending = command_line_ending if command_line_ending is not None else fill_space
            lines.append(command + cmd_ending)
        else:
            lines.append(command)

        for i, opt in enumerate(options):
            opt_lines = opt.to_lines()
            # Use per-option line_ending if specified, otherwise use default fill_space
            opt_fill_space = opt.line_ending if opt.line_ending is not None else fill_space
            for ol in opt_lines:
                if i < len(options) - 1:
                    lines.append(ol + opt_fill_space)
                else:
                    lines.append(ol)

        content = "\n".join(lines) + "\n"
        self.repo.write_script(script_name, content, output_dir=output_dir)
        return content
