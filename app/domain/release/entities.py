from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    command: str = field(metadata={"ui_hidden": True})
    update: str = field(metadata={"ui_hidden": True})
    release: str = field(metadata={"ui_hidden": True})
    prjType: str = field(metadata={"label": "Project Type","ui_hidden": True})
    prj: str = field(metadata={"label": "Project"})
    rel: str = field(metadata={"label": "Rel"})
    NoPvt: int = field(metadata={"label": "Number of PVT","divide": "versions"})
    dataRelease: str = field(metadata={"label": "Data Release Path"})
    p4_ws: str = field(metadata={"label": "Perforce Workspace"})
    lcVersion: str = field(metadata={"label": "LC Version", "divide": "versions"})
    synVersion: str = field(metadata={"label": "Synthesis Version", "divide": "versions"})
    note: str = field(metadata={"label": "Release Note"})
    flow: str = field(metadata={"label": "Flow Type","divide": "versions"})
    # mode: Literal["serial", "parallel"] = field(metadata={"label": "Execution Mode","divide": "versions"})
    serial: bool = field(default=False, metadata={"tick": True, "label": "Execute in Serial Mode","divide": "versions"})
    cell_lst: str = field(default="", metadata={"label": "Cell List Path", "placeholder": "path/to/dwc_cells.lst", "editor": True, "browser": True})
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig(
            command="bsub -Is -app quick -n 1 -M 100G -R \"select[os_version= CS7.0] span[hosts=1] rusage[mem=10GB,scratch_free=5]\" -J release_job /depot/Python/Python-3.8.0/bin/python TimingCloseBeta.py",
            update="",
            release="",
            prj="",
            rel="",
            prjType="ucie",
            NoPvt=16,
            dataRelease="",
            p4_ws=f"/remote/in01sgnfs00142/{__import__('getpass').getuser()}/p4_ws/",
            lcVersion="lc/2022.03-SP1",
            synVersion="syn/2021.06-SP1",
            note="",
            flow="auto",
            # mode="serial",
            serial=False,
        )
