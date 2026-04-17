"""Use case for getting testbench status with PVT breakdown."""
from typing import List
from app.domain.qc.entities import PVTRowMeta
from app.infrastructure.qc.testbench_repository_fs import TestbenchRepositoryFS
from app.infrastructure.fs.timing_paths import TimingPaths


class GetTestbenchStatusUseCase:
    """Get execution status for a testbench across all PVTs."""
    
    def execute(self, project: str, subproject: str, cell: str, testbench: str) -> dict:
        """
        Return per-PVT status for a testbench.
        
        Args:
            project: Project name
            subproject: Subproject name
            cell: Cell name
            testbench: Testbench directory name
            
        Returns:
            dict with project, subproject, cell, testbench, pvts, status, optional note
            
        Raises:
            FileNotFoundError: If testbench directory doesn't exist
        """
        # Resolve testbench root directory (handles canonical/legacy paths)
        tp = TimingPaths(project, subproject)
        tb_root = tp.qc_testbench_root(cell, testbench)
        
        if not tb_root.exists():
            raise FileNotFoundError(f"Testbench directory not found: {tb_root}")
        
        # Get PVT statuses from infrastructure
        tb_repo = TestbenchRepositoryFS()
        pvt_results: List[PVTRowMeta] = tb_repo.list_pvts(str(tb_root))
        
        if not pvt_results:
            return {
                "project": project,
                "subproject": subproject,
                "cell": cell,
                "testbench": testbench,
                "pvts": [],
                "status": "Not Started",
                "note": "No PVT subdirectories"
            }
        
        # Aggregate overall status
        statuses = {p.status for p in pvt_results}
        
        if "Fail" in statuses:
            agg_status = "Fail"
        elif statuses == {"Passed"}:
            agg_status = "Passed"
        elif "In Progress" in statuses:
            agg_status = "In Progress"
        else:
            agg_status = "Not Started"
        
        return {
            "project": project,
            "subproject": subproject,
            "cell": cell,
            "testbench": testbench,
            "pvts": pvt_results,
            "status": agg_status
        }
