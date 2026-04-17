"""Static analysis helper to flag potentially unused modules, functions, classes, and globals.

Enhancements:
 - FastAPI route handlers auto-marked used.
 - Router modules (under routers/ or containing an APIRouter instance) marked used if included in main.py via import.
 - Whitelist directive: place a comment '# unused: keep' immediately above a def/class/assignment to force keep.
 - Anything referenced by name (identifier, call target, attribute) counted as usage.

Heuristics & Limitations:
 - Does not parse Jinja templates yet (planned option).
 - Dynamic imports, reflection, or string indirection may cause false positives.
 - Module usage still conservative: imported name's top-level defs may be actually unused internally.

Usage:
    python -m app.utils.find_unused [--json]
"""

from __future__ import annotations

import ast
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


@dataclass
class SymbolDef:
    name: str
    file: str
    lineno: int
    kind: str  # function|class|assign
    used: bool = False
    detail: str = ""


class UsageCollector(ast.NodeVisitor):
    def __init__(self):
        self.names: Set[str] = set()
        self.called: Set[str] = set()
        self.attr_names: Set[str] = set()

    def visit_Name(self, node: ast.Name):  # noqa: N802
        self.names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):  # noqa: N802
        # Collect function being called if it's a simple name
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            # Record attribute access chain components
            self.attr_names.add(node.func.attr)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):  # noqa: N802
        self.attr_names.add(node.attr)
        self.generic_visit(node)


ROUTE_DECORATORS = {"get", "post", "put", "delete", "patch", "options", "head"}


def is_route_handler(func: ast.FunctionDef) -> bool:
    for dec in func.decorator_list:
        # Look for patterns like router.get("/path") or app.get("/path")
        target = None
        if isinstance(dec, ast.Call):
            target = dec.func
        elif isinstance(dec, ast.Attribute):
            target = dec
        if isinstance(target, ast.Attribute):
            if target.attr in ROUTE_DECORATORS:
                return True
    return False


def _has_unused_keep(lines: List[str], lineno: int) -> bool:
    """Check preceding non-empty/comment lines up to 3 lines for whitelist directive."""
    # lineno is 1-based; lines list is 0-based
    start = max(0, lineno - 4)
    for i in range(start, lineno - 1):
        text = lines[i].strip()
        if not text:
            continue
        if text.startswith('#') and 'unused: keep' in text:
            return True
        # Stop if hit a real code line before directive
        if not text.startswith('#'):
            break
    return False


def gather_definitions(file_path: str) -> List[SymbolDef]:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return []  # Skip problematic files
    defs: List[SymbolDef] = []
    lines = content.splitlines()
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            keep = _has_unused_keep(lines, node.lineno)
            detail = "route" if is_route_handler(node) else "function"
            defs.append(SymbolDef(node.name, file_path, node.lineno, "function", detail=detail, used=keep))
        elif isinstance(node, ast.ClassDef):
            keep = _has_unused_keep(lines, node.lineno)
            defs.append(SymbolDef(node.name, file_path, node.lineno, "class", used=keep))
        elif isinstance(node, ast.Assign):
            # Only simple name or UPPER_CASE targets
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    if tgt.id.startswith("_"):  # ignore private
                        continue
                    keep = _has_unused_keep(lines, tgt.lineno)
                    defs.append(SymbolDef(tgt.id, file_path, tgt.lineno, "assign", used=keep))
    return defs


def collect_usage(file_path: str) -> UsageCollector:
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return UsageCollector()
    collector = UsageCollector()
    collector.visit(tree)
    return collector


def relative(path: str) -> str:
    return os.path.relpath(path, APP_ROOT).replace(os.sep, "/")


def _generate_prune_patch(unused_syms: List[SymbolDef]) -> str:
    """Create a unified-style patch proposal for removing unused functions/classes.

    We only remove entire function/class definitions (no assignments).
    """
    by_file: Dict[str, List[SymbolDef]] = {}
    for s in unused_syms:
        if s.kind not in {"function", "class"}:
            continue
        by_file.setdefault(s.file, []).append(s)
    patch_chunks: List[str] = []
    for file, symbols in by_file.items():
        # Read file lines to isolate blocks
        with open(file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # Parse AST to map starting line to ending line
        try:
            tree = ast.parse(''.join(lines), filename=file)
        except SyntaxError:
            continue
        spans: Dict[int, int] = {}
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                # Use node.end_lineno if Python >=3.8; fallback crude scan
                end = getattr(node, 'end_lineno', None)
                if end is None:
                    # Fallback: advance until blank line after lineno
                    end_idx = node.lineno - 1
                    while end_idx + 1 < len(lines) and lines[end_idx + 1].strip():
                        end_idx += 1
                    end = end_idx + 1
                spans[node.lineno] = end
        file_patch: List[str] = []
        for sym in symbols:
            start = sym.lineno
            end = spans.get(start)
            if not end:
                continue
            # Build removal chunk (context 2 lines before/after)
            pre_start = max(0, start - 3)
            post_end = min(len(lines), end + 2)
            context_before = ''.join(lines[pre_start:start-1])
            removed_block = ''.join(lines[start-1:end])
            context_after = ''.join(lines[end:post_end])
            file_patch.append(f"--- {file}\n+++ {file} (pruned)\n@@ unused prune @@\n{context_before}" + ''.join(f"-" + l for l in removed_block.splitlines(True)) + context_after)
        if file_patch:
            patch_chunks.extend(file_patch)
    return '\n'.join(patch_chunks)


def main(argv: List[str]) -> int:
    # Discover python files under app/* excluding __pycache__
    python_files: List[str] = []
    for root, _dirs, files in os.walk(APP_ROOT):
        if "__pycache__" in root:
            continue
        for name in files:
            if name.endswith(".py"):
                python_files.append(os.path.join(root, name))

    # Build definitions index
    definitions: Dict[str, List[SymbolDef]] = {}
    all_defs: List[SymbolDef] = []
    for fp in python_files:
        defs = gather_definitions(fp)
        definitions[fp] = defs
        all_defs.extend(defs)

    # Usage aggregation
    used_names: Set[str] = set()
    for fp in python_files:
        col = collect_usage(fp)
        used_names.update(col.names)
        used_names.update(col.called)
        used_names.update(col.attr_names)

    reasons: Dict[Tuple[str, str], str] = {}
    for sym in all_defs:
        key = (sym.file, sym.name)
        if sym.kind == "function" and sym.detail == "route":
            sym.used = True
            reasons[key] = "fastapi-route"
        elif sym.used:  # pre-marked by whitelist keep
            reasons[key] = "whitelist"
        elif sym.name in used_names:
            sym.used = True
            reasons[key] = "referenced"

    # Module usage: gather imported base names + router modules included in main.py
    imported_modules: Set[str] = set()
    router_modules_in_main: Set[str] = set()
    main_path = os.path.join(APP_ROOT, "main.py")
    for fp in python_files:
        with open(fp, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read(), filename=fp)
            except SyntaxError:
                continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module.split(".")[0])
            # Detect APIRouter instantiation to mark module as router
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                    if node.value.func.id == 'APIRouter':
                        base = os.path.splitext(os.path.basename(fp))[0]
                        imported_modules.add(base)  # treat router as used

    # Parse main.py specifically for routers imported from app.routers
    if os.path.exists(main_path):
        with open(main_path, 'r', encoding='utf-8') as f:
            try:
                m_tree = ast.parse(f.read(), filename=main_path)
            except SyntaxError:
                m_tree = None
        if m_tree:
            for node in ast.walk(m_tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.endswith('.routers'):
                    for alias in node.names:
                        router_modules_in_main.add(alias.name)

    imported_modules.update(router_modules_in_main)

    # Determine unused symbols
    unused_functions = [sym for sym in all_defs if sym.kind == "function" and not sym.used]
    unused_classes = [sym for sym in all_defs if sym.kind == "class" and not sym.used]
    unused_assigns = [sym for sym in all_defs if sym.kind == "assign" and not sym.used]

    # Potentially unused modules (not imported, excluding main.py and __init__.py)
    module_candidates: List[str] = []
    for fp in python_files:
        base = os.path.splitext(os.path.basename(fp))[0]
        if base in {"__init__", "main"}:
            continue
        if base not in imported_modules:
            # Exclude routers if they define APIRouter (already treated) – quick text check
            try:
                text = open(fp, 'r', encoding='utf-8').read()
                if 'APIRouter(' in text:
                    continue
            except Exception:
                pass
            module_candidates.append(fp)

    report = {
        "unused_functions": [
            {"name": s.name, "file": relative(s.file), "line": s.lineno} for s in unused_functions
        ],
        "unused_classes": [
            {"name": s.name, "file": relative(s.file), "line": s.lineno} for s in unused_classes
        ],
        "unused_assignments": [
            {"name": s.name, "file": relative(s.file), "line": s.lineno} for s in unused_assigns
        ],
        "possibly_unused_modules": [relative(p) for p in module_candidates],
        "summary": {
            "total_functions": sum(1 for s in all_defs if s.kind == "function"),
            "total_classes": sum(1 for s in all_defs if s.kind == "class"),
            "total_assigns": sum(1 for s in all_defs if s.kind == "assign"),
        },
        "used_reasons": [
            {
                "name": s.name,
                "file": relative(s.file),
                "line": s.lineno,
                "kind": s.kind,
                "reason": reasons.get((s.file, s.name), "")
            }
            for s in all_defs if s.used
        ],
    }

    if "--prune-dry-run" in argv:
        if unused_functions or unused_classes:
            patch = _generate_prune_patch(unused_functions + unused_classes)
            print(patch)
        else:
            print("No removable symbols found.")
        return 0

    if "--json" in argv or "--json-details" in argv:
        print(json.dumps(report, indent=2))
    else:
        print("Unused functions (excluding route handlers):")
        for item in report["unused_functions"]:
            print(f"  {item['name']}  ({item['file']}:{item['line']})")
        if not report["unused_functions"]:
            print("  <none>")
        print()
        print("Unused classes:")
        for item in report["unused_classes"]:
            print(f"  {item['name']}  ({item['file']}:{item['line']})")
        if not report["unused_classes"]:
            print("  <none>")
        print()
        print("Unused top-level assignments:")
        for item in report["unused_assignments"]:
            print(f"  {item['name']}  ({item['file']}:{item['line']})")
        if not report["unused_assignments"]:
            print("  <none>")
        print()
        print("Possibly unused modules (not imported elsewhere):")
        for mod in report["possibly_unused_modules"]:
            print(f"  {mod}")
        if not report["possibly_unused_modules"]:
            print("  <none>")
        print()
        print("Summary:")
        for k, v in report["summary"].items():
            print(f"  {k}: {v}")
        print()
        print("Used symbol reasons (first 10):")
        for item in report["used_reasons"][:10]:
            print(f"  {item['name']} ({item['kind']}) -> {item['reason']}")
        print()
        print("NOTE: This is heuristic. Dynamic usage, template references, or reflection can cause false positives. Review before deletion.")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
