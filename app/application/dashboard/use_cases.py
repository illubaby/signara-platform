"""Application use cases for dashboard navigation.

Orchestrates domain logic for retrieving navigation structure.
No direct framework dependencies - pure orchestration.
"""
from app.domain.dashboard.entities import Page, NavigationMenu


class GetNavigationMenu:
    """Use case for retrieving the application navigation menu.
    
    This is a simple use case that returns the configured page structure.
    In a more complex scenario, this might read from a config file or database,
    but for now it encapsulates the hard-coded menu definition.
    """
    
    # Hard-coded menu definition following the existing PAGES structure
    _DEFAULT_PAGES = [
        Page(page_id="timing-saf", title="Timing SAF", template_name="timing_saf.html"),
        Page(page_id="timing-post-edit", title="Timing Post-edit", template_name="timing_post_edit.html"),
        Page(page_id="timing-qc", title="Timing QC", template_name="timing_qc.html"),
        Page(page_id="timing-qa", title="Timing QA", template_name="timing_qa.html"),
        # Page(page_id="timing-qa-process", title="Timing QA (Process)", template_name="timing_qa_v2.html"),
        Page(page_id="internal-timing", title="Internal Timing", template_name="generic_page.html"),
        Page(page_id="terminal", title="Terminal", template_name="terminal.html"),
        Page(page_id="explorer", title="Explorer", template_name="explorer.html"),
        Page(page_id="package-compare", title="Package Compare", template_name="package_compare.html"),
        Page(page_id="special-check", title="Special Check", template_name="special_check.html"),
        Page(page_id="compare-project", title="Compare Project", template_name="generic_page.html"),
        Page(page_id="project-status", title="Project Status", template_name="generic_page.html"),
        Page(page_id="project-release", title="Project Release", template_name="project_release.html"),
        # Note: collect-depot has dedicated router with custom form logic (collect_depot_router.py)
        Page(page_id="project-seeding", title="Project Seeding", template_name="generic_page.html"),
        Page(page_id="project-wrap-up", title="Project Wrap-up", template_name="wrap_up.html"),
    ]
    
    def execute(self) -> NavigationMenu:
        """Retrieve the navigation menu structure.
        
        Returns:
            NavigationMenu containing all available pages
        """
        return NavigationMenu(pages=self._DEFAULT_PAGES)
    
    def get_page(self, page_id: str) -> Page | None:
        """Retrieve a specific page by ID.
        
        Args:
            page_id: The page identifier to look up
            
        Returns:
            Page if found, None otherwise
        """
        menu = self.execute()
        return menu.get_page_by_id(page_id)
