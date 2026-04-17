"""Checklist repository protocol."""
from typing import Protocol, Optional
from .entities import Checklist


class ChecklistRepository(Protocol):
    """Protocol for checklist data access."""
    
    def get_checklist(self, project: str) -> Optional[Checklist]:
        """Get checklist for a project. Returns None if not found."""
        ...
    
    def save_checklist(self, project: str, checklist: Checklist) -> bool:
        """Save checklist for a project. Returns True if successful."""
        ...
    
    def ensure_checklist_exists(self, project: str) -> bool:
        """Ensure checklist file exists in P4, create if missing. Returns True if successful."""
        ...
