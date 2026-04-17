from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
REPO_PARENT = next(
	(parent for parent in SCRIPT_PATH.parents if (parent / "app" / "__init__.py").exists()),
	None,
)
if REPO_PARENT is None:
	raise RuntimeError("Unable to locate repository parent for the 'app' package")
if str(REPO_PARENT) not in sys.path:
	sys.path.insert(0, str(REPO_PARENT))

from app.application.saf.job_script_use_cases import GenerateJobScript, GenerateJobScriptInput
from app.application.saf.netlist_use_cases import SyncNetlist, SyncNetlistInput
from app.application.saf.pre_run_use_cases import (
	EnsureCellConfig,
	EnsureCellConfigInput,
	EnsureCellDirectories,
	EnsureCellDirectoriesInput,
	EnsureNetlistPresent,
	EnsureNetlistPresentInput,
)
from app.application.saf.symlink_use_cases import EnsureSafSymlinks, EnsureSafSymlinksInput
from app.infrastructure.fs.project_root import PROJECTS_BASE
from app.infrastructure.p4.saf_perforce_repository_p4 import SafPerforceRepositoryP4


def prepare_setup(project: str, subproject: str, cell: str, cell_type: str = "sis") -> dict:
	started_at = time.perf_counter()

	dirs_out = EnsureCellDirectories().execute(
		EnsureCellDirectoriesInput(
			project=project,
			subproject=subproject,
			cell=cell,
			cell_type=cell_type,
		)
	)

	cfg_out = EnsureCellConfig().execute(
		EnsureCellConfigInput(
			project=project,
			subproject=subproject,
			cell=cell,
			cell_type=cell_type,
			cell_dir=dirs_out.cell_dir,
		)
	)

	netlist_out = EnsureNetlistPresent().execute(
		EnsureNetlistPresentInput(
			project=project,
			subproject=subproject,
			cell=cell,
			cell_type=cell_type,
			cell_dir=dirs_out.cell_dir,
		)
	)

	symlink_out = EnsureSafSymlinks().execute(
		EnsureSafSymlinksInput(
			project=project,
			subproject=subproject,
			cell_root=dirs_out.cell_root,
			cell_dir=dirs_out.cell_dir,
			cell_type=cell_type,
		)
	)

	script_out = GenerateJobScript().execute(
		GenerateJobScriptInput(
			project=project,
			subproject=subproject,
			cell=cell,
			cell_type=cell_type,
				script_name=f"run_simulation_{cell}.csh",
			write=True,
			base_root=PROJECTS_BASE / project / subproject,
		)
	)

	return {
		"project": project,
		"subproject": subproject,
		"cell": cell,
		"cell_type": cell_type,
		"timing_saf_step": "prepare_setup",
		"cell_root": str(dirs_out.cell_root),
		"cell_dir": str(dirs_out.cell_dir),
		"directories": {
			"root_created": dirs_out.root_created,
			"cell_created": dirs_out.cell_created,
			"note": dirs_out.note,
		},
		"config": {
			"synced": cfg_out.synced,
			"file_found": cfg_out.file_found,
			"file_name": cfg_out.file_name,
			"note": cfg_out.note,
			"error": cfg_out.error,
		},
		"netlist": {
			"found": netlist_out.found,
			"checked_path": str(netlist_out.checked_path),
			"note": netlist_out.note,
			"error": netlist_out.error,
		},
		"symlinks": {
			"notes": symlink_out.notes,
			"warnings": symlink_out.warnings,
		},
		"job_script": {
			"path": str(script_out.script_path),
			"file_name": script_out.script_path.name,
			"created": script_out.script_path.exists(),
			"bytes_written": script_out.bytes_written,
			"exec_cmd": script_out.exec_cmd,
			"note": script_out.note,
		},
		"duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
	}


def sync_netlist(project: str, subproject: str, cell: str, cell_type: str = "sis") -> dict:
	started_at = time.perf_counter()

	out = SyncNetlist(SafPerforceRepositoryP4()).execute(
		SyncNetlistInput(
			project=project,
			subproject=subproject,
			cell=cell,
			cell_type=cell_type,
		)
	)

	local_path = PROJECTS_BASE / project / subproject / "design" / "timing" / "extr" / cell
	local_path = local_path / "nt" / "etm" if cell_type == "nt" else local_path / "sis"

	return {
		"project": project,
		"subproject": subproject,
		"cell": cell,
		"cell_type": cell_type,
		"timing_saf_step": "sync_netlist",
		"depot_path": out.depot_path,
		"checked_local_path": str(local_path),
		"checked_local_exists": local_path.exists(),
		"synced": out.synced,
		"file_count": out.file_count,
		"return_code": out.return_code,
		"stdout": out.stdout,
		"stderr": out.stderr,
		"note": out.note,
		"duration_ms": round((time.perf_counter() - started_at) * 1000, 2),
	}


def main() -> int:
	parser = argparse.ArgumentParser(description="ETM SAF helper")
	parser.add_argument("function", choices=["prepare_setup", "sync_netlist"])
	parser.add_argument("project")
	parser.add_argument("subproject")
	parser.add_argument("cell")
	parser.add_argument("cell_type", choices=["sis", "nt"])
	args = parser.parse_args()

	functions = {
		"prepare_setup": prepare_setup,
		"sync_netlist": sync_netlist,
	}
	result = functions[args.function](args.project, args.subproject, args.cell, args.cell_type)
	json.dump(result, sys.stdout, indent=2)
	return 0


if __name__ == "__main__":
	raise SystemExit(main())
