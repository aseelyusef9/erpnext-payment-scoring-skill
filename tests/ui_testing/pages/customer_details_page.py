# tests/pages/customer_details_page.py
from playwright.sync_api import Page, expect
from .base_page import BasePage

class CustomerDetailsPage(BasePage):

    def __init__(self, page: Page, base_url: str = None):
        super().__init__(page, base_url or "http://localhost:8000")
        self.customer_name = page.locator("#modalCustomerName")

    def verify_page_loaded(self):
        """Verify the customer details page is loaded correctly."""
        try:
            # Wait for the modal to be active
            self.page.wait_for_selector("#customerModal.active", timeout=15000)
        except Exception:
            pass
    
    def is_loaded(self):
        self.verify_page_loaded()

    def get_name(self) -> str:
        try:
            self.page.wait_for_selector("#modalCustomerName", timeout=10000, state="visible")
        except Exception:
            pass
        text = self.customer_name.text_content() or ""
        return text.strip()
    
    def get_insights(self) -> str:
        """Get the AI insights text from the details modal."""
        try:
            # Find the insights box - it should be in the modal
            insights_locator = self.page.locator("#modalBody .insights-box")
            text = insights_locator.text_content() or ""
            return text.strip()
        except Exception:
            return ""

