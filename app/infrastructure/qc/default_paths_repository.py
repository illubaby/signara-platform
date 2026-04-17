"""Infrastructure repository for deriving QC default paths and parsing runall.csh.

Implements QCDefaultsRepository port.
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional
import re

from app.domain.qc.entities import QCDefaultPaths
from app.domain.qc.repositories import QCDefaultsRepository
from app.infrastructure.fs.project_root import PROJECTS_BASE

class DefaultPathsRepositoryFS(QCDefaultsRepository):
    def parse_runall(self, runall_path: str) -> Dict[str, Any]:
        path = Path(runall_path)
        if not path.exists():
            return {}
        try:
            content = path.read_text()
        except Exception:
            return {}
        # Remove commented portions per line
        active_lines = []
        for line in content.splitlines():
            if '#' in line:
                line = line[:line.index('#')]
            if line.strip():
                active_lines.append(line)
        active_content = '\n'.join(active_lines)
        config: Dict[str, Any] = {}
        simple_flags = {
            'update': r'-update\s',
            'adjustment': r'-adjustment\s',
            'xtalk_rel_net': r'-xtalkRelNet\s',
            'no_wf': r'-noWF\s',
        }
        for key, pattern in simple_flags.items():
            if re.search(pattern, active_content):
                config[key] = True
        patterns = {
            'qcplan_path': r'-specs\s+(\S+)',
            'data_path': r'-data\s+(\S+)',
            'common_source_path': r'-common_source\s+(\S+)',
            'netlist_path': r'-netlist\s+(\S+)',
            'ref_data_path': r'-refdata\s+(\S+)',
            'debug_path': r'-debug\s+(\S+)',
            'include': r'-include\s+(\S+)',
            'hierarchy': r'-hierarchy\s+(\S+)',
            'verbose': r'-verbose\s+(\S+)',
            'xtalk': r'-xtalk\s+(\S+)',
            'primesim': r'-primesim\s+(\S+)',
            'hspice': r'-hspice\s+(\S+)',
        }
        for key, pattern in patterns.items():
            m = re.search(pattern, active_content)
            if m:
                config[key] = m.group(1).rstrip('\\').strip()
        
        # Handle multiple -datastore entries
        datastore_matches = re.findall(r'-datastore\s+(\S+)', active_content)
        if datastore_matches:
            config['datastore_paths'] = [ds.rstrip('\\').strip() for ds in datastore_matches]
        
        qm = re.search(r'-index\s+"([^"]+)"', active_content)
        if qm:
            config['index'] = qm.group(1)
        qm = re.search(r'-phase\s+"([^"]+)"', active_content)
        if qm:
            config['phase'] = qm.group(1)
        return config

    def _qcplan_path_for_cell(self, cell: str, project: str) -> str:
        if project.startswith('h') and len(project) > 1:
            digit = project[1]
            if digit == '1':
                gen = 'gr_ucie'
            elif digit == '2':
                gen = 'gr_ucie2_v2'
            elif digit == '3':
                gen = 'gr_ucie3_v1'
            else:
                gen = 'gr_ucie2_v2'
        else:
            if 'ucie2phy' in cell:
                gen = 'gr_ucie2_v2'
            elif 'ucie3phy' in cell:
                gen = 'gr_ucie3_v1'
            elif 'uciephy' in cell:
                gen = 'gr_ucie'
            else:
                gen = 'gr_ucie2_v2'
        return f"//wwcad/msip/projects/ucie/tb/{gen}/design/timing/qc/{cell}_QcPlan.xlsx"

    def derive_defaults(self, project: str, subproject: str, cell: str, force_defaults: bool = False) -> QCDefaultPaths:
        root = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'quality' / '4_qc' / cell
        internal_node_map_path = root / 'TMQC_internal_node.map'
        runall_path = root / 'runall.csh'
        parsed = {} if force_defaults else (self.parse_runall(str(runall_path)) if runall_path.exists() else {})
        if parsed:
            return QCDefaultPaths(
                qcplan_path=parsed.get('qcplan_path'),
                netlist_path=parsed.get('netlist_path'),
                data_path=parsed.get('data_path'),
                datastore_paths=parsed.get('datastore_paths'),
                common_source_path=parsed.get('common_source_path'),
                timing_paths_path=None,
                ref_data_path=parsed.get('ref_data_path'),
                update=parsed.get('update', False),
                adjustment=parsed.get('adjustment', False),
                no_wf=parsed.get('no_wf', False),
                xtalk_rel_net=parsed.get('xtalk_rel_net', False),
                hierarchy=parsed.get('hierarchy'),
                verbose=parsed.get('verbose'),
                include=parsed.get('include'),
                xtalk=parsed.get('xtalk'),
                primesim=parsed.get('primesim'),
                hspice=parsed.get('hspice'),
                index=parsed.get('index', '0 2 3'),
                phase=parsed.get('phase', 'specs clear setup'),
                debug_path=parsed.get('debug_path'),
                tmqc_internal_node_map_path=str(internal_node_map_path),
                note='Loaded from runall.csh'
            )
        qcplan = self._qcplan_path_for_cell(cell, project)
        netlist_dir = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'extr' / cell / 'sis'
        common_source_path = f"/remote/cad-rep/projects/ucie/{project}/{subproject}/design/timing/sis/common_source/"
        default_data_root = PROJECTS_BASE / project / subproject / 'design' / 'timing' / 'release' / 'internal'
        default_data_path = default_data_root / 'raw_lib'
        timing_paths_dir = root / 'timing_paths'
        refdata_path = root / 'ref' / 'refdata.csv'
        return QCDefaultPaths(
            qcplan_path=qcplan,
            netlist_path=str(netlist_dir),
            data_path=str(default_data_path),
            datastore_paths=None,
            common_source_path=common_source_path,
            timing_paths_path=str(timing_paths_dir) if timing_paths_dir.exists() else None,
            ref_data_path=str(refdata_path) if refdata_path.exists() else None,
            update=False,
            adjustment=True,
            no_wf=True,
            xtalk_rel_net=False,
            hierarchy=None,
            verbose=None,
            include=None,
            xtalk=None,
            primesim=None,
            hspice=None,
            index='0 2 3',
            phase='specs clear setup',
            debug_path=None,
            tmqc_internal_node_map_path=str(internal_node_map_path),
            note='Default values'
        )

__all__ = ["DefaultPathsRepositoryFS"]