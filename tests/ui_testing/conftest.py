import os
import subprocess
import time
import requests
import unittest
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import BrowserFactory for test base class
from tests.ui_testing.BrowserFactory import BrowserFactory

# Load environment variables from .env file FIRST
load_dotenv(override=True)

# Ensure environment variables are set early
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("USE_MOCK_DATA", "False")


class UITestBase(unittest.TestCase):
    """
    Base class for UI tests with browser and server setup/teardown.
    
    Handles:
    - Loading and verifying ERPNext + Claude AI credentials
    - Starting FastAPI UI server (if needed)
    - Creating BrowserFactory and Playwright page instances
    - Cleaning up resources after tests
    
    Environment variables supported:
    - BROWSER: chromium (default), firefox, webkit
    - HEADLESS: true (default), false
    - SCREEN_WIDTH: viewport width (default: 1920)
    - SCREEN_HEIGHT: viewport height (default: 1080)
    - UI_SLOW_MO_MS: slow motion milliseconds (default: 400)
    - UI_BASE_URL: base URL for the application (default: http://localhost:8000)
    - UI_SKIP_SERVER: if 'true', don't start local server
    - UI_HEALTH_PATH: path for health checks (default: /health)
    - USE_MOCK_DATA: if 'false', use real ERPNext data (default: True)
    """
    
    browser_factory = None
    page = None
    context = None
    server_process = None
    base_url = None
    
    @classmethod
    def setUpClass(cls):
        """
        Set up class-level resources before running any tests.
        
        - Verify ERPNext and Claude AI credentials
        - Start FastAPI server if needed
        - Create BrowserFactory instance
        """
        # Verify ERPNext credentials are loaded
        erpnext_url = os.getenv("ERPNEXT_URL")
        erpnext_key = os.getenv("ERPNEXT_API_KEY")
        erpnext_secret = os.getenv("ERPNEXT_API_SECRET")
        
        if not all([erpnext_url, erpnext_key, erpnext_secret]):
            print("\n[WARNING] ERPNext credentials not fully configured in .env")
            print(f"  ERPNEXT_URL: {erpnext_url or 'NOT SET'}")
            print(f"  ERPNEXT_API_KEY: {'SET' if erpnext_key else 'NOT SET'}")
            print(f"  ERPNEXT_API_SECRET: {'SET' if erpnext_secret else 'NOT SET'}")
        else:
            print("\n[OK] ERPNext credentials loaded successfully")
            print(f"  ERPNEXT_URL: {erpnext_url}")
        
        # Verify Claude AI credentials are loaded
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_key:
            print("[WARNING] ANTHROPIC_API_KEY not configured - AI features will be disabled")
        else:
            print("[OK] Claude AI credentials loaded successfully")
        
        # Verify USE_MOCK_DATA setting
        use_mock = os.getenv("USE_MOCK_DATA", "False").lower() == "true"
        print(f"[INFO] Using {'MOCK' if use_mock else 'REAL'} data for tests")
        
        # Start UI server if needed
        cls._start_ui_server()
        
        # Store base_url as class attribute for access in test methods
        cls.base_url = os.getenv("UI_BASE_URL", "http://localhost:8000")
        
        # Create BrowserFactory instance
        cls.browser_factory = BrowserFactory()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up class-level resources after all tests have run."""
        # Close browser
        if cls.browser_factory:
            try:
                cls.browser_factory.close()
            except Exception as e:
                print(f"Error closing browser factory: {e}")
        
        # Stop server
        if cls.server_process:
            try:
                cls.server_process.terminate()
                cls.server_process.wait(timeout=5)
            except Exception:
                try:
                    cls.server_process.kill()
                except Exception:
                    pass
    
    def setUp(self):
        """Set up instance-level resources before each test."""
        # Create a fresh page for each test using the class-level browser factory
        if self.browser_factory and self.browser_factory.browser:
            try:
                # Create new context and page in existing browser
                self.context = self.browser_factory.browser.new_context(
                    viewport={
                        'width': int(os.getenv('SCREEN_WIDTH', '1920')),
                        'height': int(os.getenv('SCREEN_HEIGHT', '1080'))
                    }
                )
                self.page = self.context.new_page()
            except Exception as e:
                print(f"Warning: failed to create page from existing browser: {e}")
                # Fallback: create new page through factory (creates new browser)
                self.page = self.browser_factory.create_page()
                self.context = self.browser_factory.context
        else:
            # Fallback: create new page through factory
            self.page = self.browser_factory.create_page()
            self.context = self.browser_factory.context
    
    def tearDown(self):
        """Clean up instance-level resources after each test."""
        # Close page first
        if self.page:
            try:
                # Cancel any pending navigations or requests
                try:
                    self.page.close()
                except Exception:
                    pass
            except Exception:
                pass
        
        # Then close context
        if self.context:
            try:
                self.context.close()
            except Exception:
                pass
        
        # Clear references
        self.page = None
        self.context = None
        
        # Longer delay to ensure cleanup and server recovery
        time.sleep(2)
    
    @classmethod
    def _start_ui_server(cls):
        """
        Ensure the FastAPI UI server is running for UI tests.
        
        Tries to hit /health; if unavailable, starts uvicorn and waits until healthy.
        """
        base_url = os.environ.get("UI_BASE_URL", "http://localhost:8000")
        # Allow external frontend: skip starting local server when requested
        ui_skip_server = os.environ.get("UI_SKIP_SERVER", "False").lower() == "true"
        # Configurable health path; empty disables health checks entirely
        health_path = os.environ.get("UI_HEALTH_PATH", "/health")
        health_url = (f"{base_url}{health_path}" if health_path else None)

        # If skipping server, don't try to start uvicorn
        if ui_skip_server:
            # Optionally wait for external health if provided
            if health_url:
                for _ in range(30):
                    try:
                        resp = requests.get(health_url, timeout=2)
                        if resp.status_code == 200:
                            print("[OK] External server is healthy")
                            return
                    except Exception:
                        time.sleep(1)
            return

        # Check if server is already running
        if health_url:
            for _ in range(5):
                try:
                    resp = requests.get(health_url, timeout=2)
                    if resp.status_code == 200:
                        print("[OK] Server already running at", base_url)
                        return
                except Exception:
                    time.sleep(1)

        # Server not running, so start it
        print(f"[INFO] Starting UI server at {base_url}")
        cls.server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False,
            env=os.environ.copy(),  # Pass current environment to subprocess
        )

        # Wait for server to become healthy (if health checks enabled)
        if health_url:
            max_wait = 90
            for attempt in range(max_wait):
                try:
                    resp = requests.get(health_url, timeout=2)
                    if resp.status_code == 200:
                        print(f"[OK] Server started successfully (waited {attempt} seconds)")
                        return
                except Exception:
                    pass
                time.sleep(1)
            
            print(f"[WARNING] Server did not become healthy after {max_wait} seconds")
        else:
            # No health checks, just wait a bit
            time.sleep(3)
            print("[OK] Server started (no health check configured)")