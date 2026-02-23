from config.config import Config


class BrowserConfig:
    def __init__(self, playwright):
        self.config = Config()
        self.playwright = playwright

    def launch_browser(self):
        browser_type = self.config.get_browser_type()
        headless_mode = self.config.is_headless()

        browsers = {
            "chromium": self.playwright.chromium,
            "firefox": self.playwright.firefox,
            "webkit": self.playwright.webkit,
        }

        if browser_type not in browsers:
            raise ValueError(f"Unsupported browser type: {browser_type}")

        return browsers[browser_type].launch(headless=headless_mode)
