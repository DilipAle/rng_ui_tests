from playwright.sync_api import sync_playwright
from config.config import Config

class BrowserConfig:
    def __init__(self, playwright: sync_playwright):
        self.config = Config()  # Get the configuration
        self.playwright = playwright  # Save playwright instance for use

    def launch_browser(self):
        """Launch the browser using Playwright."""
        browser_type = self.config.get_browser_type()  # Fetch browser type from config
        headless_mode = self.config.is_headless()  # Fetch headless mode from config
        
        # Launch the browser with the given settings
        if browser_type == "chromium":
            return self.playwright.chromium.launch(headless=headless_mode)
        elif browser_type == "firefox":
            return self.playwright.firefox.launch(headless=headless_mode)
        elif browser_type == "webkit":
            return self.playwright.webkit.launch(headless=headless_mode)
        else:
            raise ValueError(f"Unsupported browser type: {browser_type}")