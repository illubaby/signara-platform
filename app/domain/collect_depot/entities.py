from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    collectdepot: str = field( metadata={"ui_hidden": True})
    database: str = field(metadata={"label": "Database"})
    rel: str = field(metadata={"label": "rel"})
    cell: str = field(metadata={"label": "Cell List File", "editor": True, "browser": True})
    cfg: str = field(metadata={"label": "Config File", "placeholder": "Optional config file path", "optional": True})

    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="TimingCloseBeta.py",
            update="",
            collectdepot="",
            database="",
            rel="",
            cell="",
            cfg=""
        )
