"""
shared/browser_config.py
=========================
Handles Playwright browser launch for all UI projects.

Reads BROWSER and HEADLESS settings from Config and launches
the correct browser type. Supports chromium, firefox, and webkit.

Used by conftest.py in each UI project:
    browser_config = BrowserConfig(playwright)
    browser = browser_config.launch_browser()
"""

from playwright.sync_api import sync_playwright
from shared.config import Config


class BrowserConfig:
    """
    Launches a Playwright browser instance based on config settings.

    Supported browsers (set BROWSER= in .env):
        chromium  → Google Chrome / Microsoft Edge (default, recommended)
        firefox   → Mozilla Firefox
        webkit    → Apple Safari engine

    Headless mode (set HEADLESS= in .env):
        true  → No visible browser window. Always use this in CI/CD.
        false → Opens a real browser window. Use when debugging locally.

    Usage in conftest.py:
        with sync_playwright() as playwright:
            browser_config = BrowserConfig(playwright)
            browser = browser_config.launch_browser()
            page = browser.new_page()
    """

    def __init__(self, playwright):
        """
        Args:
            playwright: The sync_playwright context manager instance
                        passed in from conftest.py
        """
        self.config = Config()
        self.playwright = playwright

    def launch_browser(self):
        """
        Launch and return a browser instance using settings from Config.

        Returns:
            Browser: A Playwright browser instance

        Raises:
            ValueError: If BROWSER is set to an unsupported value
        """
        browser_type = self.config.get_browser_type()
        headless_mode = self.config.is_headless()

        # Map browser name string to Playwright browser object
        browsers = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }

        if browser_type not in browsers:
            raise ValueError(f"Unsupported browser type: {browser_type}. Choose from: chromium, firefox, webkit")

        return browsers[browser_type].launch(headless=headless_mode)
