from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    
    command: str = field(default="./bin/python/bbSimGuiNT_Batch/lib/run_all_preps.py", metadata={"ui_hidden": True})
    block_path: Literal["dummy"] = field(default="", metadata={"label": "Block Path", "include_attribute": True,"divide": "versions"})
    sim: str = field(default="", metadata={"label": "PVT Selection", "ui_hidden": True, "optional": True})
    setup: bool = field(default=False, metadata={"tick": True, "ui_hidden": True, "label": "Setup"})
    reload: bool = field(default=False, metadata={"tick": True, "ui_hidden": True, "label": "Reload"})
    
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig()
