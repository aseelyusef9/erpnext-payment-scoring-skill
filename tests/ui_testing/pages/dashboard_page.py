# tests/pages/dashboard_page.py
import os
from playwright.sync_api import Page, expect
from .base_page import BasePage


class DashboardPage(BasePage):

    def __init__(self, page: Page, base_url: str = None):
        if base_url is None:
            base_url = os.environ.get("UI_BASE_URL", "http://localhost:8000")
        super().__init__(page, base_url)

        self.high_risk_tab = page.get_by_text("High Risk")
        self.search_input = page.get_by_placeholder("Search customers...")
        self.rows = page.locator("table tbody tr")
        self.risk_badges = page.locator("table tbody tr td:nth-child(3) .badge")

    def open(self):
        force_ai = os.environ.get("UI_FORCE_AI", "False").lower() == "true"
        path = "/dashboard" + ("?ai=1" if force_ai else "")
        try:
            self.page.goto(f"{self.base_url}{path}", wait_until="domcontentloaded", timeout=90000)
        except Exception as e:
            print(f"[WARNING] Page.goto timeout or error: {e}")
            # Try one more time with networkidle
            try:
                self.page.goto(f"{self.base_url}{path}", wait_until="networkidle", timeout=30000)
            except Exception as e2:
                print(f"[ERROR] Second attempt failed: {e2}")
                raise
        
        # Handle ngrok warning page if present
        try:
            self.page.get_by_role("button", name="Visit Site").click(timeout=3000)
            print("[INFO] Clicked ngrok 'Visit Site' button")
            # Wait for page to load after clicking
            self.page.wait_for_load_state("domcontentloaded", timeout=30000)
        except Exception:
            pass  # Ngrok warning page was not loaded
        
        try:
            # Wait for data rows to render (View Details button present)
            # Increased timeout for real ERPNext + AI in CI (can take 60+ seconds)
            self.page.wait_for_selector("table tbody tr button:has-text('View Details')", timeout=120000)
        except Exception:
            pass

    def verify_page_loaded(self):
        """Verify the dashboard is loaded correctly."""
        expect(self.page.locator(".brand-name")).to_be_visible()
    
    def is_loaded(self):
        self.verify_page_loaded()

    def filter_high_risk(self):
        # Click the High Risk tab button
        self.page.get_by_role("button", name="High Risk").click()
        
        # Wait for the API call to complete and data to render
        # First, wait for any loading spinners to disappear or actual data to appear
        try:
            # Wait for the table to have actual data rows (not just loading message)
            # This will wait until we see a View Details button or a "No customers found" message
            self.page.wait_for_function(
                """() => {
                    const viewDetailsButtons = document.querySelectorAll("table tbody tr button");
                    const buttonsWithText = Array.from(viewDetailsButtons).filter(btn => btn.textContent.includes('View Details'));
                    const noCustMsg = document.body.innerText.includes("No customers found");
                    return buttonsWithText.length > 0 || noCustMsg;
                }""",
                timeout=30000
            )
        except Exception as e:
            print(f"Warning: timeout waiting for high-risk filter results: {e}")
        
        try:
            # Give a bit more time for rendering
            self.page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            pass

    def only_high_risk_visible(self) -> bool:
        # Ensure table has rows and every risk badge shows 'high'
        try:
            self.page.wait_for_selector("table tbody tr td:nth-child(3) .badge", timeout=10000)
        except Exception:
            pass
        badges = [txt.strip().lower() for txt in self.risk_badges.all_text_contents()]
        return len(badges) > 0 and set(badges) == {"high"}

    def visible_risk_levels(self):
        # Return list of risk levels shown in the table's third column
        try:
            self.page.wait_for_selector("table tbody tr td:nth-child(3) .badge", timeout=10000)
        except Exception:
            pass
        return [txt.strip().lower() for txt in self.risk_badges.all_text_contents()]

    def search_customer(self, name: str):
        self.search_input.fill(name)
        # Allow table to update after search
        try:
            self.page.wait_for_load_state("networkidle", timeout=3000)
        except Exception:
            pass

    def open_first_customer(self):
        btn = self.page.get_by_role("button", name="View Details").first
        try:
            btn.scroll_into_view_if_needed()
        except Exception:
            pass
        try:
            btn.click()
        except Exception as e:
            print(f"Failed to click button: {e}")
            raise
        # Wait for modal to be shown and populated
        try:
            self.page.wait_for_selector("#customerModal.active", timeout=15000)
        except Exception:
            pass
        try:
            # Wait for the insights-box inside the modal (indicates async data loaded)
            self.page.wait_for_selector("#modalBody .insights-box", timeout=20000, state="visible")
        except Exception:
            pass

    def get_rows_count(self):
        # Count only data rows that have 'View Details' button
        return self.page.locator("table tbody tr button:has-text('View Details')").count()

    def first_row_text(self):
        try:
            self.page.wait_for_selector("table tbody tr button:has-text('View Details')", timeout=15000)
        except Exception:
            pass
        text = self.rows.first.text_content()
        return text or ""

    def first_customer_name(self):
        try:
            self.page.wait_for_selector("table tbody tr button:has-text('View Details')", timeout=15000)
        except Exception:
            pass
        row = self.rows.first
        # First cell contains customer name in the first div
        name_locator = row.locator("td").first.locator("div").first
        name = name_locator.text_content() or ""
        return name.strip()

    def visible_risk_levels(self):
        badges = self.page.locator("table tbody tr td:nth-child(3) .badge")
        try:
            self.page.wait_for_selector("table tbody tr td:nth-child(3) .badge", timeout=10000)
        except Exception:
            pass
        levels = [t.strip().lower() for t in badges.all_text_contents()]
        return levels
