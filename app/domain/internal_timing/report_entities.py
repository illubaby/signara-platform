from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(default="bsub -Is -app quick -n 1 -M 100G -R \"span[hosts=1] rusage[mem=10GB,scratch_free=5]\" -J internal_timing_job /depot/Python/Python-3.8.0/bin/python TimingCloseBeta.py", metadata={"ui_hidden": True})
    internal: str = field(default="", metadata={"ui_hidden": True})
    cell: str = field(default="", metadata={"label": "Cell Name", "placeholder": "cell_name"})
    queue: str = field(default="normal", metadata={"label": "Queue", "placeholder": "queue_name","divide": "versions"})
    data: str = field(default="", metadata={"label": "Data Directory", "browser": True})
    noWF: bool = field(default=True, metadata={"tick": True,"divide": "versions"})
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
        )
