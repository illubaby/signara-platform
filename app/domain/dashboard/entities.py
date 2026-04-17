"""Domain entities for dashboard navigation and page configuration.

Pure business logic representing the application's page structure.
No framework dependencies allowed - only stdlib.
"""
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Page:
    """Represents a navigable page in the application.
    
    Attributes:
        page_id: URL-safe identifier (e.g., 'timing-saf')
        title: Human-readable display name (e.g., 'Timing SAF')
        template_name: Template filename without path (e.g., 'timing_saf.html')
    """
    page_id: str
    title: str
    template_name: str
    
    def __post_init__(self):
        """Validate domain invariants."""
        if not self.page_id or not self.page_id.strip():
            raise ValueError("Page ID cannot be empty")
        if not self.title or not self.title.strip():
            raise ValueError("Title cannot be empty")
        if not self.template_name or not self.template_name.strip():
            raise ValueError("Template name cannot be empty")
        if not self.template_name.endswith('.html'):
            raise ValueError("Template name must end with .html")


@dataclass(frozen=True)
class NavigationMenu:
    """Collection of navigable pages forming the application menu.
    
    Attributes:
        pages: List of pages available in the navigation
    """
    pages: List[Page]
    
    def __post_init__(self):
        """Validate menu structure."""
        if not self.pages:
            raise ValueError("Navigation menu must contain at least one page")
        
        # Check for duplicate page IDs
        page_ids = [p.page_id for p in self.pages]
        if len(page_ids) != len(set(page_ids)):
            raise ValueError("Duplicate page IDs detected in navigation menu")
    
    def get_page_by_id(self, page_id: str) -> Page | None:
        """Retrieve a page by its ID.
        
        Args:
            page_id: The page identifier to search for
            
        Returns:
            Page if found, None otherwise
        """
        return next((p for p in self.pages if p.page_id == page_id), None)
    
    def get_page_title(self, page_id: str, default: str = "") -> str:
        """Get the title for a page ID.
        
        Args:
            page_id: The page identifier
            default: Default value if page not found
            
        Returns:
            Page title or default value
        """
        page = self.get_page_by_id(page_id)
        return page.title if page else default
