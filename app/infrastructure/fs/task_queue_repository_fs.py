"""Task Queue Repository - Filesystem implementation.

Handles reading and writing task queue configuration files:
- sis_task_queue.tcl
- monte_carlo_settings.tcl (optional)
"""
from pathlib import Path
from typing import Dict, Tuple
from app.domain.task_queue.entities import TaskQueueConfig, TaskQueueResult, TaskQueueStatus


class TaskQueueRepositoryFS:
    """Filesystem-based task queue repository."""
    
    def write_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str,
        config: TaskQueueConfig
    ) -> TaskQueueResult:
        """Write task queue configuration files to cell directory."""
        sis_task_queue_path = cell_dir / "sis_task_queue.tcl"
        monte_path = cell_dir / "monte_carlo_settings.tcl"
        existed_before = sis_task_queue_path.exists()
        
        try:
            content, sim = self._build_sis_task_queue_content(config)
            sis_task_queue_path.write_text(content)
            bytes_task = sis_task_queue_path.stat().st_size
        except Exception as e:
            raise RuntimeError(f"Failed writing sis_task_queue.tcl: {e}")
        
        bytes_monte = None
        monte_written = None
        if config.write_monte_carlo:
            try:
                monte_content = self._build_monte_carlo_content(config)
                monte_path.write_text(monte_content)
                bytes_monte = monte_path.stat().st_size
                monte_written = str(monte_path)
            except Exception as e:
                raise RuntimeError(f"Failed writing monte_carlo_settings.tcl: {e}")
        
        note = (
            ("Updated existing " if existed_before else "Generated ") +
            ("sis_task_queue.tcl and monte_carlo_settings.tcl" if monte_written else "sis_task_queue.tcl")
        )
        
        return TaskQueueResult(
            project=project,
            subproject=subproject,
            cell=cell,
            sis_task_queue_path=str(sis_task_queue_path),
            bytes_written_task_queue=bytes_task,
            monte_carlo_settings_path=monte_written,
            bytes_written_montecarlo=bytes_monte,
            simulator=sim,
            note=note,
        )
    
    def read_task_queue(
        self,
        cell_dir: Path,
        project: str,
        subproject: str,
        cell: str
    ) -> TaskQueueStatus:
        """Read existing task queue configuration from cell directory."""
        tq_path = cell_dir / "sis_task_queue.tcl"
        mc_path = cell_dir / "monte_carlo_settings.tcl"
        
        tq_values = self._parse_taskqueue_file(tq_path)
        mc_values = self._parse_monte_file(mc_path)
        
        # Start with defaults
        config_data = {
            "normal_queue_no_prefix": "1",
            "job_scheduler": "lsf",
            "run_list_maxsize": "100",
            "normal_queue": '-app normal -n 1 -M 100G -R "span[hosts=1] rusage[mem=10GB,scratch_free=15]"',
            "statistical_montecarlo_sample_size": "250",
            "netlist_max_sweeps": "1000",
            "simulator": "primesim",
            "write_monte_carlo": True,
        }
        
        # Overlay existing values from sis_task_queue.tcl
        for k in ("normal_queue_no_prefix", "job_scheduler", "run_list_maxsize", "normal_queue"):
            if k in tq_values:
                config_data[k] = tq_values[k]
        
        # Determine simulator
        sim = 'primesim'
        if 'simulator' in tq_values:
            sim_lower = tq_values['simulator'].lower()
            if sim_lower in ('primesim', 'hspice'):
                sim = sim_lower
        config_data['simulator'] = sim
        
        # Overlay Monte Carlo settings
        if 'statistical_montecarlo_sample_size' in mc_values:
            config_data['statistical_montecarlo_sample_size'] = mc_values['statistical_montecarlo_sample_size']
        if 'netlist_max_sweeps' in mc_values:
            config_data['netlist_max_sweeps'] = mc_values['netlist_max_sweeps']
        if 'statistical_simulation_points' in mc_values:
            config_data['statistical_simulation_points'] = mc_values['statistical_simulation_points']
        
        config = TaskQueueConfig(**config_data)
        
        return TaskQueueStatus(
            project=project,
            subproject=subproject,
            cell=cell,
            exists_task_queue=tq_path.exists(),
            exists_monte_carlo=mc_path.exists(),
            config=config,
            simulator=sim,
            sis_task_queue_path=str(tq_path) if tq_path.exists() else None,
            monte_carlo_settings_path=str(mc_path) if mc_path.exists() else None,
            note=None,
        )
    
    def _build_sis_task_queue_content(self, config: TaskQueueConfig) -> Tuple[str, str]:
        """Build sis_task_queue.tcl content. Returns (content, simulator)."""
        lines = [
            f"set normal_queue_no_prefix {config.normal_queue_no_prefix}",
            f"set job_scheduler {config.job_scheduler}",
            f"set run_list_maxsize {config.run_list_maxsize}",
            f"set normal_queue {{{config.normal_queue}}}",
        ]
        if config.simulator.lower() == "hspice":
            lines.append("#SIMULATOR: HSPICE")
            lines.append("set simulator hspice")
            lines.append("set simulator_cmd {hspice <input_deck> -o <listing_file>}")
            sim = "hspice"
        else:
            lines.append("#SIMULATOR: PRIMESIM")
            lines.append("set simulator primesim")
            lines.append("set simulator_cmd {primesim -spice <input_deck> -o <listing_file> -runlvl 6 -hsp}")
            sim = "primesim"
        return ("\n".join(lines) + "\n", sim)
    
    def _build_monte_carlo_content(self, config: TaskQueueConfig) -> str:
        """Build monte_carlo_settings.tcl content."""
        points = config.statistical_simulation_points
        # Ensure points are wrapped in braces for TCL list formatting
        if not (points.startswith("{") and points.endswith("}")):
            points = "{" + points.strip() + "}"
        return "\n".join([
            f"set_config_opt statistical_montecarlo_sample_size {config.statistical_montecarlo_sample_size}",
            f"set_config_opt netlist_max_sweeps {config.netlist_max_sweeps}",
            f"set_config_opt statistical_simulation_points {points}",
        ]) + "\n"
    
    def _parse_taskqueue_file(self, path: Path) -> Dict[str, str]:
        """Parse sis_task_queue.tcl file."""
        values: Dict[str, str] = {}
        if not path.exists():
            return values
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(None, 2)
                if len(parts) >= 3 and parts[0] == 'set':
                    key = parts[1]
                    val = parts[2]
                    if val.startswith('{') and val.endswith('}'):
                        val = val[1:-1]
                    values[key] = val
        except Exception:
            return values
        return values
    
    def _parse_monte_file(self, path: Path) -> Dict[str, str]:
        """Parse monte_carlo_settings.tcl file."""
        values: Dict[str, str] = {}
        if not path.exists():
            return values
        try:
            for line in path.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(None, 2)
                if len(parts) >= 3 and parts[0] == 'set_config_opt':
                    key = parts[1]
                    val = parts[2]
                    values[key] = val
        except Exception:
            return values
        return values
