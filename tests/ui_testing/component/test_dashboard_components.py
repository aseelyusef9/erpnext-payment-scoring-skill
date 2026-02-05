import unittest
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.ui_testing.conftest import UITestBase
from tests.ui_testing.pages.dashboard_page import DashboardPage


class TestDashboardComponents(UITestBase):
    """Component tests for dashboard UI elements."""
    
    @classmethod
    def setUpClass(cls):
        """Setup: Use mock data for fast component testing."""
        # Set mock data and skip AI BEFORE calling parent (so it's used when server starts)
        os.environ["USE_MOCK_DATA"] = "True"
        os.environ["SKIP_AI_ANALYSIS"] = "True"  # Skip Claude AI for fast tests
        os.environ["UI_FORCE_AI"] = "False"
        
        # Make browser visible and slow down actions to see what's happening
        os.environ["HEADLESS"] = "false"
        os.environ["UI_SLOW_MO_MS"] = "200"  # 200ms delay - fast but still visible
        os.environ["SCREEN_WIDTH"] = "1366"  # Adjust to your screen width
        os.environ["SCREEN_HEIGHT"] = "768"  # Adjust to your screen height
        
        # Force server restart by stopping any running server first
        # This ensures the server picks up the new environment variables
        if hasattr(UITestBase, 'server_process') and UITestBase.server_process:
            try:
                UITestBase.server_process.terminate()
                UITestBase.server_process.wait(timeout=5)
                print("[OK] Stopped previous server to enable mock data + fast scoring")
            except Exception:
                try:
                    UITestBase.server_process.kill()
                except Exception:
                    pass
            UITestBase.server_process = None
        
        super().setUpClass()
        
        print("[OK] Component test configuration: Mock data enabled, AI disabled, fast scoring enabled")

    def setUp(self):
        """Set up each test with a fresh page and dashboard."""
        super().setUp()
        self.dashboard = DashboardPage(self.page, self.base_url)
        self.dashboard.open()

    def test_dashboard_loads(self):
        self.dashboard.verify_page_loaded()

    def test_high_risk_tab_filters(self):
        self.dashboard.filter_high_risk()
        self.assertGreater(self.dashboard.get_rows_count(), 0)

    def test_search_component(self):
        name = self.dashboard.first_customer_name()
        self.assertTrue(len(name) > 0)
        self.dashboard.search_customer(name)
        self.assertIn(name, self.dashboard.first_row_text())

    def test_view_details_button_exists(self):
        button = self.page.get_by_role("button", name="View Details").first
        self.assertTrue(button.is_visible())


if __name__ == '__main__':
    unittest.main()
