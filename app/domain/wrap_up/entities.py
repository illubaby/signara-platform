from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    sync: str = field(metadata={"ui_hidden": True})
    prj: str = field(metadata={"ui_hidden": True})
    mode: Literal["snapshot", "submit"] = field(metadata={"label": "Execution Mode"})
    setup: list[str] = field(default_factory=list, metadata={"label": "Setup", "ui_multi": True, "placeholder": " "})

    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="TimingCloseBeta.py",
            update="",
            sync="",
            prj="",
            mode="snapshot-design",
            setup=[],
        )
