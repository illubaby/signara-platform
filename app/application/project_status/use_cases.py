"""Use cases for Project Status feature (PIC editing)."""
from dataclasses import dataclass
from typing import Optional, Iterable, List, Dict, Any

from app.domain.cell.repositories import CellRepository
from app.domain.terminal.repositories import TerminalCommandRunner
import logging
import sys
import platform


@dataclass
class UpdateCellPicInput:
	project: str
	subproject: str
	cell: str
	pic: Optional[str]


class UpdateCellPic:
	def __init__(self, repo: CellRepository):
		self.repo = repo

	def execute(self, inp: UpdateCellPicInput) -> bool:
		if not inp.project or not inp.subproject or not inp.cell:
			raise ValueError("project, subproject, and cell must be provided")
		return self.repo.update_cell_pic(inp.project, inp.subproject, inp.cell, inp.pic)


@dataclass
class BatchUpdateCellPicInput:
	project: str
	subproject: str
	updates: Iterable[tuple[str, Optional[str]]]


class BatchUpdateCellPic:
	def __init__(self, repo: CellRepository):
		self.repo = repo

	def execute(self, inp: BatchUpdateCellPicInput) -> int:
		if not inp.project or not inp.subproject:
			raise ValueError("project and subproject must be provided")
		# Use batch method to avoid multiple P4 uploads
		return self.repo.batch_update_cell_pic(inp.project, inp.subproject, inp.updates)


@dataclass
class BatchUpdateCellFieldsInput:
	project: str
	subproject: str
	updates: Iterable[tuple[str, dict]]


class BatchUpdateCellFields:
	def __init__(self, repo: CellRepository):
		self.repo = repo

	def execute(self, inp: BatchUpdateCellFieldsInput) -> int:
		if not inp.project or not inp.subproject:
			raise ValueError("project and subproject must be provided")
		return self.repo.batch_update_cell_fields(inp.project, inp.subproject, inp.updates)


# -------------------------------
# JIRA Refresh
# -------------------------------

@dataclass
class RefreshJiraStatusInput:
	project: str
	subproject: str
	workdir: Optional[str] = None
	timeout_seconds: int = 180


class RefreshJiraStatus:
	"""Runs external JIRA status script for each cell's jira_link and updates assignee/duedate/status fields.

	Minimal policy:
	- For multiple jira links on a cell, process in given order
	- Concatenate values per field using ", " in the processed order
	- Skip cells with empty/no jira_link
	- Ignore links that fail to return valid JSON
	"""

	def __init__(self, repo: CellRepository, runner: TerminalCommandRunner):
		self.repo = repo
		self.runner = runner
		self._logger = logging.getLogger(__name__)

	@staticmethod
	def _parse_issues(stdout: str) -> List[Dict[str, Any]]:
		"""Try to parse JSON array from stdout, returning list of issue dicts."""
		import json
		try:
			data = json.loads(stdout)
			if isinstance(data, list):
				return [d for d in data if isinstance(d, dict)]
			return []
		except Exception:
			return []

	def execute(self, inp: RefreshJiraStatusInput) -> int:
		if not inp.project or not inp.subproject:
			raise ValueError("project and subproject must be provided")

		# Load current cells (no forced refresh; we only enrich cached file)
		self._logger.info(f"[RefreshJiraStatus] Start: project={inp.project}, subproject={inp.subproject}")
		self._logger.debug(f"[RefreshJiraStatus] Environment: os={platform.system()} python={sys.executable} workdir={inp.workdir}")
		cells = self.repo.list_cells(inp.project, inp.subproject, refresh=False)
		self._logger.debug(f"[RefreshJiraStatus] Loaded {len(cells)} cells from cache")

		updates: List[tuple[str, dict]] = []

		def _safe_filename(name: str) -> str:
			return ''.join(ch if ch.isalnum() or ch in ('-', '_') else '_' for ch in (name or 'cell'))

		for cell in cells:
			jira = (cell.jira_link or '').strip()
			if not jira:
				continue

			# Support multiple links separated by whitespace
			links: List[str] = [p for p in jira.split() if p]
			assignees: List[str] = []
			duedates: List[str] = []
			statuses: List[str] = []

			# Prepare deterministic output file per cell
			out_name = f"{_safe_filename(cell.ckt_macros)}.json"
			import os
			out_path = os.path.normpath(os.path.join(inp.workdir or os.getcwd(), out_name))
			self._logger.debug(f"[RefreshJiraStatus] Using output file: {out_path}")

			self._logger.debug(f"[RefreshJiraStatus] Cell={cell.ckt_macros} links={links}")
			for link in links:
				# Clean previous output to avoid stale reads
				try:
					if os.path.exists(out_path):
						os.remove(out_path)
						self._logger.debug(f"[RefreshJiraStatus] Removed stale output: {out_path}")
				except Exception as re:
					self._logger.warning(f"[RefreshJiraStatus] Failed to remove stale output {out_path}: {re}")

				# Prefer executing the script directly to honor its shebang.
				# On Windows, use bash if available so shebang is respected.
				script_rel = "../bin/python/my_app/taskmanager/jirastatus.py"
				if platform.system().lower() == 'windows':
					cmd = f"bash -lc '{script_rel} -o \"{out_name}\" \"{link}\"'"
					mode = 'bash'
				else:
					cmd = f"{script_rel} -o \"{out_name}\" \"{link}\""
					mode = 'direct'
				self._logger.debug(f"[RefreshJiraStatus] Running command (mode={mode}): {cmd} (cwd={inp.workdir})")
				result = self.runner.run(cmd, timeout=inp.timeout_seconds, workdir=inp.workdir)
				self._logger.debug(
					f"[RefreshJiraStatus] ReturnCode={result.return_code} Duration={result.duration:.2f}s Truncated={result.truncated}"
				)
				if result.return_code not in (0, None):
					err_preview = (result.stderr or "").splitlines()
					err_preview = " | ".join(err_preview[:3])
					self._logger.warning(f"[RefreshJiraStatus] Non-zero exit; stderr (first lines): {err_preview}")
					# Fallback: try current Python interpreter if bash/direct failed
					fallback_cmd = f"\"{sys.executable}\" {script_rel} -o \"{out_name}\" \"{link}\""
					self._logger.debug(f"[RefreshJiraStatus] Fallback running: {fallback_cmd}")
					result = self.runner.run(fallback_cmd, timeout=inp.timeout_seconds, workdir=inp.workdir)
					self._logger.debug(
						f"[RefreshJiraStatus][Fallback] ReturnCode={result.return_code} Duration={result.duration:.2f}s"
					)

				# Read per-cell output file deterministically
				issues: List[Dict[str, Any]] = []
				try:
					if os.path.exists(out_path):
						import json
						with open(out_path, 'r') as f:
							data = json.load(f)
							if isinstance(data, list):
								issues = [d for d in data if isinstance(d, dict)]
						self._logger.debug(f"[RefreshJiraStatus] Read {len(issues)} issue(s) from {out_name}")
					else:
						self._logger.warning(f"[RefreshJiraStatus] Output file missing: {out_name}")
				except Exception as fe:
					self._logger.warning(f"[RefreshJiraStatus] Failed reading {out_name}: {fe}")
    
				# Keep order as generated per link
				for it in issues:
					a = (it.get("Assignee") or "").strip()
					d = (it.get("Duedate") or "").strip()
					s = (it.get("Status") or "").strip()
					if a:
						assignees.append(a)
					if d:
						duedates.append(d)
					if s:
						statuses.append(s)

			if assignees or duedates or statuses:
				updates.append((cell.ckt_macros, {
					"assignee": "\n".join(assignees) if assignees else "",
					"duedate": "\n".join(duedates) if duedates else "",
					"status": "\n".join(statuses) if statuses else "",
				}))

		if not updates:
			self._logger.info("[RefreshJiraStatus] No updates parsed from JIRA outputs")
			return 0

		# Persist via existing batch fields updater
		batch_uc = BatchUpdateCellFields(self.repo)
		updated_count = batch_uc.execute(BatchUpdateCellFieldsInput(project=inp.project, subproject=inp.subproject, updates=updates))
		self._logger.info(f"[RefreshJiraStatus] Updated fields for {updated_count} cell(s)")
		return updated_count
