"""QA repository protocol - defines the contract for QA data access."""
from typing import Protocol, List, Optional
from pathlib import Path
from .entities import QACell, QASummary, QADefaults, QARunRequest, QARunResult, QAJobStatus, CellCheckMatrix


class QARepository(Protocol):
    """Port for QA operations."""
    
    def list_cells(self, project: str, subproject: str) -> List[QACell]:
        """List all QA cells for a project/subproject."""
        ...
    
    def get_defaults(self, project: str, subproject: str, cell: Optional[str], qa_type: str = 'quality') -> QADefaults:
        """Get default parameters for QA execution.
        
        Args:
            qa_type: 'quality' or 'process' to determine default run directory
        """
        ...
    
    def get_available_cells(self, data_release_path: str) -> List[str]:
        """Get list of cells from data release directory."""
        ...
    
    def get_summary(self, project: str, subproject: str, cell: str) -> QASummary:
        """Get QA summary for a specific cell."""
        ...
    
    def run_qa(self, project: str, subproject: str, request: QARunRequest) -> QARunResult:
        """Execute QA checks and return result."""
        ...
    
    def get_job_status(self, job_id: str) -> Optional[QAJobStatus]:
        """Get status of a running QA job."""
        ...
    
    def get_matrix_summary(self, project: str, subproject: str, run_dir: str) -> CellCheckMatrix:
        """Get QA matrix summary from brief.sum files in run directory."""
        ...


# Display checks configuration (domain constant)
DISPLAY_CHECKS: List[str] = [
    "msip_hipreLibAreaCorrect",
    "msip_hipreLibGenDb",
    "msip_hipreLibOperCondCheck",
    "LCQA_lib_screener",
    "UCIeQA",
    "extract_max_tran_cap",
    "hbi_libs_vs_plan",
    "hbi_libs_skewcheck",
    "msip_hipreLibFileNameVsLibraryDef",
    "msip_hipreLibPinCapacitanceCheck",
    "msip_hipreLibConsistencyCheck",
    "msip_hipreLibPGPinCheck",
    "msip_hipreLibReadInDC",
    "msip_hipreLibVsDbCheck",
    "msip_hipreLibVsLib",
    "msip_hipreLibCheckSetupHoldTrend",
    "msip_hipreLibertyCheck",
    "msip_hipreLibPinAttributesCheck",
    "msip_hipreLibUPFAttributesCheck",
    "msip_hipreLibCompare",
    "msip_hipreLibVsLef",
    "msip_hipreLibVsVerilog",
    "msip_hipreLibPinFunctionCheck",
    "msip_hipreLibModesCheck",
    "msip_hipreLibTimingArcCheck",
    "pincheck_wo_csv",
    "pincheck_wo_lef",
    "pincheck_wo_verilog",
]

MANDATORY_CHECKS: List[str] = DISPLAY_CHECKS[:3]
