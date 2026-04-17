from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(default="bsub -Is -app quick -n 1 -M 100G -R \"span[hosts=1] rusage[mem=10GB,scratch_free=5]\" -J postedit_job /depot/Python/Python-3.8.0/bin/python TimingCloseBeta.py", metadata={"ui_hidden": True})
    # update: str = field(default="", metadata={"ui_hidden": True})
    postedit: str = field(default="", metadata={"ui_hidden": True})
    cell: str = field(default="", metadata={"label": "Cell Name", "placeholder": "cell_name"})
    lib: str = field(default="", metadata={"label": "Lib path", "placeholder": "path/to/lib", "browser": True})
    output: str = field(default="Postedit_Output", metadata={"label": "Output Directory", "placeholder": "path/to/outputdir", "browser": True})
    plan: str = field(default="", metadata={"label": "Plan XLSX", "placeholder": "constraint.xlsx", "optional": True})
    configfile: str = field(default="", metadata={"label": "Config File", "placeholder": "path/to/configfile", "editor": True, "browser": True})
    cell_lst: str = field(default="", metadata={"label": "List Cell", "placeholder": "path/to/dwc_cells.lst", "editor": True, "browser": True, "exclude_option": True})
    configfile_multiple_cells: str = field(default="", metadata={"label": "Config Folder for multiple cells", "placeholder": "<config_folder>/<cellname>/<cellname>.cfg", "browser": True, "exclude_option": True})
    
    reference: str = field(default="", metadata={"label": "Reference Directory", "placeholder": "optional", "browser": True, "optional": True})
    reformat_mode: Literal["reformat sis", "reformat pt"] = field(default="reformat pt", metadata={"label": "Reformat Type","divide": "tick", "optional": True})

    # reformat: str = field(default="pt", metadata={"label": "Reformat Type","divide": "tick"})
    pt: str = field(default="2022.12-SP5", metadata={"label": "PT Version","divide": "tick"})
    reorder: bool = field(default=False, metadata={"tick": True, "divide": "tick"})
    leakage: bool = field(default=False, metadata={"tick": True, "divide": "tick"})
    update: bool = field(default=False, metadata={"tick": True, "divide": "tick"})    
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
        )
