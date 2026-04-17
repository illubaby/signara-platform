from app.application.dashboard.use_cases import GetNavigationMenu

def get_navigation_menu_uc() -> GetNavigationMenu:
    """Factory for GetNavigationMenu use case."""
    return GetNavigationMenu()

__all__ = ["get_navigation_menu_uc"]
