from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    package: str = field(metadata={"ui_hidden": True})
    focus: str = field(metadata={"ui_hidden": True})
    test: str = field(metadata={"label": "Test"})
    ref: str = field(metadata={"label": "Ref"})
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="bsub -Is -app quick -n 1 -M 100G -R \"span[hosts=1] rusage[mem=10GB,scratch_free=5]\" -J postedit_job /depot/Python/Python-3.8.0/bin/python TimingCloseBeta.py",
            update = "",
            package="",
            focus="",
            test="",
            ref="",
        )
