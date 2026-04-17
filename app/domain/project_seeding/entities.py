from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    prj_seeding: str = field(metadata={"ui_hidden": True})
    prj_info: str = field(metadata={"label": "Project Info File"})
    ref: str = field(metadata={"label": "Reference","browser": True})
    # cell_list: str = field(metadata={"label": "Cell List File", "editor": True, "browser": True})
    mode: Literal["design", "pcs", "upload"] = field(metadata={"label": "Execution Mode"})
    updated_files: str = field(metadata={"label": "Updated Files", "editor": True, "exclude_option": True})
    # upload: bool = field(default=False, metadata={"tick": True, "label": "Upload Results to Database"})
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="TimingCloseBeta.py",
            update="",
            prj_seeding="",
            prj_info="",
            ref="",
            # cell_list="",
            mode="design",
            updated_files="",
        )
