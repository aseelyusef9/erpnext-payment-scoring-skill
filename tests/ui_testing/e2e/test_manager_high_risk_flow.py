"""E2E test for manager high-risk flow."""

import os
import time
import requests
from dotenv import load_dotenv

from tests.ui_testing.conftest import UITestBase
from tests.ui_testing.pages.dashboard_page import DashboardPage
from tests.ui_testing.pages.customer_details_page import CustomerDetailsPage


class TestManagerHighRiskFlowWithFixtures(UITestBase):
    """E2E test suite for manager high-risk flow with BrowserFactory support."""
    
    @classmethod
    def setUpClass(cls):
        """Setup: Inherit server + browser setup from UITestBase, then add UI-specific config."""
        # Call parent setUpClass to handle credentials, server startup, and browser init
        super().setUpClass()
        
        # 5. Ensure we use real data and AI for testing (UI-specific overrides)
        os.environ["USE_MOCK_DATA"] = "False"
        os.environ["UI_FORCE_AI"] = "True"
        os.environ["AI_TOPK"] = "15"
        
        print(f"[OK] UI-specific configuration loaded")

    def test_manager_reviews_high_risk_customers(self):
        """
        Test that a manager can view and filter high-risk customers.
        
        This test:
        1. Opens the dashboard
        2. Filters for high-risk customers
        3. Opens the first customer's details
        4. Verifies the modal displays correctly
        """
        # 1. Open Dashboard (assume authenticated user)
        dashboard = DashboardPage(self.page, self.base_url)
        dashboard.open()
        dashboard.verify_page_loaded()
        
        # Debug: Check initial table
        initial_rows = self.page.locator("table tbody tr").count()
        print(f"[DEBUG] Initial rows in table: {initial_rows}")

        # 2. Filter High Risk customers
        dashboard.filter_high_risk()
        
        # Debug: Check console for errors
        time.sleep(2)
        
        row_count = dashboard.get_rows_count()
        print(f"[DEBUG] Rows after filter: {row_count}")
        
        # Debug: Check the HTML of the table to see what's there
        table_html = self.page.locator("table tbody").inner_html()
        print(f"[DEBUG] Table HTML length: {len(table_html)}")
        if len(table_html) < 500:
            print(f"[DEBUG] Table HTML:\n{table_html}")
        else:
            print(f"[DEBUG] Table HTML (truncated):\n{table_html[:500]}...")
        
        self.assertGreater(
            row_count, 
            0, 
            "Expected high-risk customers to be displayed"
        )
        
        # 3. Open the first high-risk customer's details
        dashboard.open_first_customer()
        details = CustomerDetailsPage(self.page, self.base_url)
        details.verify_page_loaded()
        
        # Wait briefly for async modal data to load
        time.sleep(0.5)
        
        # 4. Verify modal opened and displays customer details
        customer_name = details.get_name()
        self.assertGreater(len(customer_name), 0, "Customer name should be displayed")
        print(f"[SUCCESS] Customer details loaded: {customer_name}")
        
        # Optionally get insights (may not always be available)
        try:
            insights = details.get_insights()
            if insights and len(insights) > 0:
                print(f"[OK] AI Insights found: {insights[:100]}...")
            else:
                print("[INFO] Insights not available (expected in some scenarios)")
        except Exception as e:
            print(f"[INFO] Insights element not found: {str(e)}")
        
        # Optional pause to observe the details
        pause_seconds = float(os.getenv("UI_PAUSE_AFTER_DETAILS", "0"))
        if pause_seconds > 0:
            time.sleep(pause_seconds)


if __name__ == "__main__":
    unittest.main()

