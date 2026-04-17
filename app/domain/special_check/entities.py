from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    special: str = field(metadata={"ui_hidden": True})
    database: str = field(metadata={"label": "Database"})
    specs: str = field(metadata={"label": "Specs File"})
    var: str = field(metadata={"label": "Var File"})

    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="TimingCloseBeta.py",
            update="",
            special="",
            database="",
            specs="",
            var=""
        )
