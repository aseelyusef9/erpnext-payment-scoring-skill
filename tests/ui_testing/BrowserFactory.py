"""Browser Factory for multi-browser and multi-resolution testing."""

import os
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright
from typing import Tuple, Optional


class BrowserFactory:
    """Factory class to create browser instances based on environment variables."""
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        # Get configuration from environment variables
        self.browser_name = os.getenv('BROWSER', 'chromium').lower()
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.screen_width = int(os.getenv('SCREEN_WIDTH', '1920'))
        self.screen_height = int(os.getenv('SCREEN_HEIGHT', '1080'))
        self.slow_mo = int(os.getenv('UI_SLOW_MO_MS', '400'))
        self.base_url = os.getenv('UI_BASE_URL', 'http://localhost:8000')
    
    def create_page(self) -> Page:
        """
        Create and return a browser page instance configured with the environment settings.
        
        Returns:
            Page: Playwright page instance
        """
        self.playwright = sync_playwright().start()
        
        # Select browser based on environment variable
        if self.browser_name == 'firefox':
            self.browser = self.playwright.firefox.launch(headless=self.headless, slow_mo=self.slow_mo)
        elif self.browser_name == 'webkit':
            self.browser = self.playwright.webkit.launch(headless=self.headless, slow_mo=self.slow_mo)
        else:  # Default to chromium
            self.browser = self.playwright.chromium.launch(headless=self.headless, slow_mo=self.slow_mo)
        
        # Create context with specified viewport
        context_options = {'viewport': {'width': self.screen_width, 'height': self.screen_height}}
        
        # If not headless, maximize the window to fit screen
        if not self.headless:
            context_options['viewport'] = None  # Use actual window size
            context_options['no_viewport'] = True
        
        self.context = self.browser.new_context(**context_options)
        
        # Create and return page
        self.page = self.context.new_page()
        return self.page
    
    def create_browser(self) -> Tuple[Browser, BrowserContext, Page]:
        """
        Legacy method: Create and configure browser instance.
        
        Returns:
            Tuple of (browser, context, page)
        """
        self.create_page()
        return self.browser, self.context, self.page
    
    def close(self):
        """Close browser and cleanup resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
