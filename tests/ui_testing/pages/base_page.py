"""Base Page Object for all page classes."""

from playwright.sync_api import Page


class BasePage:
    """Base class for all page objects with common functionality."""
    
    def __init__(self, page: Page, base_url: str):
        """
        Initialize the base page object.
        
        Args:
            page: Playwright page instance
            base_url: Base URL of the application
        """
        self.page = page
        self.base_url = base_url
    
    def verify_page_loaded(self):
        """Verify that the page is loaded correctly. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement verify_page_loaded")
    
    def clear_storage(self):
        """Clear browser storage (localStorage, sessionStorage)."""
        self.page.evaluate("localStorage.clear()")
        self.page.evaluate("sessionStorage.clear()")
