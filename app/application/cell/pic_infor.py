from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def find_first_tracklog_match(
	log_type: str,
	macro: str,
	projectname: str,
	release: str,
	file_path: str | Path | None = None,
) -> Optional[tuple[str, str, str]]:
	"""Return the first (username, workingdir, date) matching the given keys.

	If no match is found (or the file can't be read), returns None.
	"""
	if file_path is None:
		# Prefer the shared tracklog path; fall back to the repo copy.
		app_root = Path(__file__).resolve().parents[2]
		candidates = [
			Path("/u/thaison/study/timing_platform_tracklog.json"),
			app_root / "utils" / "timing_platform_tracklog.json",
		]
	else:
		candidates = [Path(file_path)]

	entries = None
	for candidate in candidates:
		try:
			with candidate.open("r", encoding="utf-8") as handle:
				entries = json.load(handle)
			break
		except Exception:
			continue

	if entries is None:
		return None

	if not isinstance(entries, list):
		return None

	for entry in entries:
		if not isinstance(entry, dict):
			continue
		if entry.get("type") != log_type:
			continue
		if entry.get("macro") != macro:
			continue

		project = entry.get("project")
		if not isinstance(project, dict):
			continue
		if project.get("projectname") != projectname:
			continue
		if project.get("release") != release:
			continue

		username = entry.get("username")
		workingdir = project.get("workingdir")
		date = entry.get("date")
		if isinstance(username, str) and isinstance(workingdir, str) and isinstance(date, str):
			return (username, workingdir, date)

	return None


@dataclass(frozen=True)
class GetPicInforInput:
	log_type: str
	macro: str
	projectname: str
	release: str
	file_path: str | Path | None = None


@dataclass(frozen=True)
class GetPicInforResult:
	username: str
	workingdir: str
	date: str


class GetPicInfor:
	def execute(self, inp: GetPicInforInput) -> Optional[GetPicInforResult]:
		match = find_first_tracklog_match(
			log_type=inp.log_type,
			macro=inp.macro,
			projectname=inp.projectname,
			release=inp.release,
			file_path=inp.file_path,
		)
		if not match:
			return None
		username, workingdir, date = match
		return GetPicInforResult(username=username, workingdir=workingdir, date=date)
