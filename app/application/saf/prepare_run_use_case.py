"""Composite use-case: prepare SAF cell environment and (optionally) run job script.

Phase 3 migration.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from app.application.saf.pre_run_use_cases import (
    EnsureCellDirectories, EnsureCellDirectoriesInput,
    EnsureCellConfig, EnsureCellConfigInput,
    EnsureNetlistPresent, EnsureNetlistPresentInput,
)
from app.application.saf.symlink_use_cases import (
    EnsureSafSymlinks, EnsureSafSymlinksInput
)
from app.infrastructure.processes.job_execution_service import JobExecutionService
from app.application.saf.job_script_use_cases import GenerateJobScript, GenerateJobScriptInput, RunJobScript, RunJobScriptInput
from app.infrastructure.fs.project_root import PROJECTS_BASE

@dataclass
class PrepareAndRunJobInput:
    project: str
    subproject: str
    cell: str
    cell_type: str
    generate: bool  # whether to generate/update script
    hspice_version: Optional[str] = None
    finesim_version: Optional[str] = None
    primesim_version: Optional[str] = None
    siliconsmart_version: Optional[str] = None
    queue: Optional[str] = None
    netlist_type: Optional[str] = None
    pvt_list: Optional[str] = None
    selected_pvts: Optional[list] = None
    raw_lib_paths: Optional[str] = None
    nt_option: Optional[str] = None
    internal_saf: bool = False
    bsub_args: Optional[str] = None
    script_name: str = "runall.csh"
    run: bool = False
    timeout: int = 300

@dataclass
class PrepareAndRunJobOutput:
    script_path: Path
    bytes_written: int
    prepared_note: str
    ran: bool
    return_code: Optional[int]
    stdout: Optional[str]
    stderr: Optional[str]
    exec_cmd: Optional[str]
    note: Optional[str]

class PrepareAndRunJob:
    def __init__(self,
                 exec_service: Optional[JobExecutionService] = None,
                 ensure_dirs_uc: Optional[EnsureCellDirectories] = None,
                 ensure_cfg_uc: Optional[EnsureCellConfig] = None,
                 ensure_net_uc: Optional[EnsureNetlistPresent] = None,
                 ensure_sym_uc: Optional[EnsureSafSymlinks] = None,
                 gen_uc: Optional[GenerateJobScript] = None,
                 run_uc: Optional[RunJobScript] = None):
        self.exec_service = exec_service or JobExecutionService()
        self.ensure_dirs_uc = ensure_dirs_uc or EnsureCellDirectories()
        self.ensure_cfg_uc = ensure_cfg_uc or EnsureCellConfig()
        self.ensure_net_uc = ensure_net_uc or EnsureNetlistPresent()
        self.ensure_sym_uc = ensure_sym_uc or EnsureSafSymlinks()
        self.gen_uc = gen_uc or GenerateJobScript()
        self.run_uc = run_uc or RunJobScript(self.exec_service)

    def execute(self, inp: PrepareAndRunJobInput) -> PrepareAndRunJobOutput:
        dirs_out = self.ensure_dirs_uc.execute(EnsureCellDirectoriesInput(project=inp.project, subproject=inp.subproject, cell=inp.cell, cell_type=inp.cell_type))
        cfg_out = self.ensure_cfg_uc.execute(EnsureCellConfigInput(project=inp.project, subproject=inp.subproject, cell=inp.cell, cell_type=inp.cell_type, cell_dir=dirs_out.cell_dir))
        net_out = self.ensure_net_uc.execute(EnsureNetlistPresentInput(project=inp.project, subproject=inp.subproject, cell=inp.cell, cell_type=inp.cell_type, cell_dir=dirs_out.cell_dir))
        sym_out = self.ensure_sym_uc.execute(EnsureSafSymlinksInput(project=inp.project, subproject=inp.subproject, cell_root=dirs_out.cell_root, cell_dir=dirs_out.cell_dir, cell_type=inp.cell_type))
        prepared_note = " | ".join([
            dirs_out.note,
            f"config: {cfg_out.note}{' ERR:'+cfg_out.error if cfg_out.error else ''}",
            f"netlist: {net_out.note}{' ERR:'+net_out.error if net_out.error else ''}",
            f"symlinks: {'; '.join(sym_out.notes)}" + (f" WARN: {'; '.join(sym_out.warnings)}" if sym_out.warnings else "")
        ])
        # script path - should be in the sis/ or nt/ directory (cell_root), not in individual cell dir
        script_path = dirs_out.cell_root / inp.script_name
        bytes_written = 0
        if inp.generate:
            gen_inp = GenerateJobScriptInput(
                project=inp.project,
                subproject=inp.subproject,
                cell=inp.cell,
                cell_type=inp.cell_type,
                hspice_version=inp.hspice_version,
                finesim_version=inp.finesim_version,
                primesim_version=inp.primesim_version,
                siliconsmart_version=inp.siliconsmart_version,
                queue=inp.queue,
                netlist_type=inp.netlist_type,
                pvt_list=inp.pvt_list,
                selected_pvts=inp.selected_pvts,
                raw_lib_paths=inp.raw_lib_paths,
                nt_option=inp.nt_option,
                bsub_args=(getattr(inp, 'bsub_args', None)),
                script_name=inp.script_name,
                internal_saf=inp.internal_saf,
                write=True,
                base_root=PROJECTS_BASE / inp.project / inp.subproject,
            )
            gen_out = self.gen_uc.execute(gen_inp)
            script_path = gen_out.script_path
            bytes_written = gen_out.bytes_written
        if inp.run:
            run_out = self.run_uc.execute(RunJobScriptInput(script_path=script_path, timeout=inp.timeout))
            note = run_out.note
            exec_cmd = f"csh {script_path}"  # approximate command (RunJobScript hides actual shell selection)
            return PrepareAndRunJobOutput(script_path=script_path, bytes_written=bytes_written, prepared_note=prepared_note, ran=True, return_code=run_out.return_code, stdout=run_out.stdout, stderr=run_out.stderr, exec_cmd=exec_cmd, note=note)
        return PrepareAndRunJobOutput(script_path=script_path, bytes_written=bytes_written, prepared_note=prepared_note, ran=False, return_code=None, stdout=None, stderr=None, exec_cmd=None, note="prepared")

__all__ = ["PrepareAndRunJob", "PrepareAndRunJobInput", "PrepareAndRunJobOutput"]
