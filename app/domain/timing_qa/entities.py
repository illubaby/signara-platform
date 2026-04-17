from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FormConfig:
    # command: str = field(default="TimingClosedBeta.py -update", metadata={"ui_hidden": True, "line_ending": ""})
    command: str = field(default="TimingCloseBeta.py -update", metadata={"ui_hidden": True, "line_ending": ""})
    # command_line: Literal["bin/python/TMQAallcells.py","dummy"] = field(default="bin/python/TMQAallcells.py", metadata={"label": "QA Command", "ui_hidden": True, "line_ending": ""})
    mode: Literal["bin/python/TMQAallcells.py"] = field(default="bin/python/TMQAallcells.py", metadata={"label": "QA Command", "ui_hidden": True, "line_ending": " \\", "no_prefix": True})

    # update: str = field(default="", metadata={"ui_hidden": True})
    data: str = field(default="", metadata={"label": "Data Path", "placeholder": "path/to/data", "browser": True})
    prj: str = field(default="", metadata={"label": "Project Name", "placeholder": "Project","divide": "versions"})
    rel: str = field(default="", metadata={"label": "Release", "placeholder": "rel","divide": "versions"})
    plan: str = field(default="", metadata={"label": "Plan XLSX", "placeholder": "constraint.xlsx"})
    celllist: str = field(default="", metadata={"label": "Cell List Path", "placeholder": "path/to/dwc_cells.lst", "editor": True, "browser": True})
    header: str = field(default="", metadata={"label": "Header File", "placeholder": "header_dummy.txt","editor": True, "browser": True})

     
    outdir: str = field(default="", metadata={"label": "Output Directory", "placeholder": ".../PostQA_libs", "browser": True})
    qsub: str = field(default="quick", metadata={"label": "Queue", "placeholder": "quick","divide": "versions"})
    noUpload: bool = field(default=False, metadata={"tick": True, "label": "Disable Upload Report"})
    # Boolean QA flags (present => True)
    msip_hipreLibAreaCorrect: bool = field(default=True, metadata={"tick": True, "group": "Library QA1", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibGenDb: bool = field(default=True, metadata={"tick": True, "group": "Library QA1", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibOperCondCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA1", "group_display": False, "check_group": "Check_Type"})
    LCQA_lib_screener: bool = field(default=True, metadata={"tick": True, "group": "Library QA1", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibTimingArcCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA1", "group_display": False, "check_group": "Check_Type"})
    UCIeQA: bool = field(default=True, metadata={"tick": True, "group": "Library QA2", "group_display": False, "check_group": "Check_Type"})
    extract_max_tran_cap: bool = field(default=True, metadata={"tick": True, "group": "Library QA2", "group_display": False, "check_group": "Check_Type"})
    hbi_libs_vs_plan: bool = field(default=True, metadata={"tick": True, "group": "Library QA2", "group_display": False, "check_group": "Check_Type"})
    hbi_libs_skewcheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA2", "group_display": False, "check_group": "Check_Type"})
    pincheck_wo_csv: bool = field(default=False, metadata={"tick": True, "group": "Library QA2", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibFileNameVsLibraryDef: bool = field(default=True, metadata={"tick": True, "group": "Library QA3", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibPinCapacitanceCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA3", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibConsistencyCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA3", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibPGPinCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA3", "group_display": False, "check_group": "Check_Type"})
    pincheck_wo_lef: bool = field(default=False, metadata={"tick": True, "group": "Library QA3", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibReadInDC: bool = field(default=True, metadata={"tick": True, "group": "Library QA4", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibVsDbCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA4", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibVsLib: bool = field(default=True, metadata={"tick": True, "group": "Library QA4", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibCheckSetupHoldTrend: bool = field(default=True, metadata={"tick": True, "group": "Library QA4", "group_display": False, "check_group": "Check_Type"})
    pincheck_wo_verilog: bool = field(default=True, metadata={"tick": True, "group": "Library QA4", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibertyCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA5", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibPinAttributesCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA5", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibUPFAttributesCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA5", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibCompare: bool = field(default=True, metadata={"tick": True, "group": "Library QA5", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibVsLef: bool = field(default=True, metadata={"tick": True, "group": "Library QA5", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibVsVerilog: bool = field(default=True, metadata={"tick": True, "group": "Library QA6", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibPinFunctionCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA6", "group_display": False, "check_group": "Check_Type"})
    msip_hipreLibModesCheck: bool = field(default=True, metadata={"tick": True, "group": "Library QA6", "group_display": False, "check_group": "Check_Type"})
    
    @staticmethod
    def default() -> "FormConfig":
        return FormConfig()
