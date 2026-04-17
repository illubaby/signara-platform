"""Router auto-discovery and registration.

This module automatically discovers all router modules in this directory
and exposes their routers for registration in main.py.
"""
import importlib
from pathlib import Path
from typing import List
from fastapi import APIRouter

# Define router registration order (optional - for dependencies/layout concerns)
# Routers not listed in either list will be registered alphabetically between ROUTER_PRIORITY and ROUTER_LAST
ROUTER_PRIORITY = [
    "version_router",      # Version check
    "access_router",       # Access type detection first
    "projects_router",     # Project selection
    "task_queue_router",   # Task infrastructure
    "execution_router",    # Execution infrastructure
    "saf_router",          # SAF main
    "saf_pvts_router",     # SAF PVTs
    "post_edit_router",    # Post-edit
    "qc_router",           # QC
    "qa_router",           # QA
    "terminal_router",     # Terminal
    # "explorer_router",     # Explorer (disabled)
    "file_picker_router",  # File picker
    "lsf_router",          # LSF
    "file_operations_router",  # File operations
    "project_status_router",   # Project status
    "release_router",      # Release
    "collect_depot_router", # Collect depot
    "wrap_up_router",      # Wrap up
    "package_compare_router", # Package compare
    "script_router",       # Script execution
    "checklist_router",    # Checklist
]

# Routers that MUST be registered last (e.g., catch-all routes)
# These will always be registered after all other routers to avoid intercepting specific routes
ROUTER_LAST = [
    "dashboard_router",    # MUST BE LAST - has catch-all /{page_id} route
]


def discover_routers() -> List[APIRouter]:
    """Auto-discover and load all routers from this directory.
    
    Registration order: ROUTER_PRIORITY → Remaining (alphabetical) → ROUTER_LAST
    This ensures catch-all routes (like dashboard's /{page_id}) don't intercept specific routes.
    
    Returns:
        List of APIRouter instances in priority order
    """
    routers = []
    router_dir = Path(__file__).parent
    
    # Get all Python files recursively except __init__.py
    router_files = []
    for f in router_dir.rglob("*.py"):
        if f.stem == "__init__" or f.stem.startswith("_"):
            continue
        rel = f.relative_to(router_dir).with_suffix("")
        module_name = ".".join(rel.parts)
        router_files.append(module_name)
    
    # Build ordered list: priority routers first, then remaining alphabetically, then last routers
    priority_routers = [r for r in ROUTER_PRIORITY if r in router_files]
    last_routers = [r for r in ROUTER_LAST if r in router_files]
    
    # Remaining routers are those not in either list
    excluded = set(ROUTER_PRIORITY) | set(ROUTER_LAST)
    remaining_routers = sorted([r for r in router_files if r not in excluded])
    
    ordered_routers = priority_routers + remaining_routers + last_routers
    
    # Import and collect routers
    for module_name in ordered_routers:
        try:
            module = importlib.import_module(f"app.interface.http.routers.{module_name}")
            if hasattr(module, "router"):
                routers.append(module.router)
        except Exception as e:
            # Log but don't fail - allows partial functionality if one router is broken
            print(f"Warning: Failed to load router from {module_name}: {e}")
    
    return routers


# Export for convenience (though main.py will call discover_routers())
__all__ = ["discover_routers", "ROUTER_PRIORITY", "ROUTER_LAST"]
