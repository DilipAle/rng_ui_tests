# pages/base_page.py
from playwright.sync_api import Page

class BasePage:
    def __init__(self, page: Page):
        self.page = page

    def wait_for_element(self, selector: str, timeout: int = 30000):
        """Waits for an element to appear on the page"""
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str):
        """Clicks on the given element"""
        self.page.click(selector)

    def fill(self, selector: str, value: str):
        """Fills the input field with the provided value"""
        self.page.fill(selector, value)

    def get_title(self):
        """Returns the page title"""
        return self.page.title()

    def goto(self, url: str):
        """Navigates to the provided URL"""
        self.page.goto(url)
