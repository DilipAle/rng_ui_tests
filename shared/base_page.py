"""
shared/base_page.py
====================
The single source of truth for all browser interaction methods.

Every page object across all 3 UI projects (renegade-ui-tests,
agency-height-tests, customer-portal-tests) inherits from this class.

Design pattern: Page Object Model (POM)
    - Tests never call Playwright directly
    - Tests call page object methods (e.g. login_page.login())
    - Page objects call BasePage methods (e.g. self.fill(), self.click())
    - BasePage calls Playwright (e.g. self.page.fill())

How to add a new method:
    1. Add it here in BasePage
    2. It becomes available in ALL page objects automatically
    3. No changes needed in individual projects
"""

from playwright.sync_api import Page


class BasePage:
    """
    Base class for all page objects.

    All page objects must inherit from this class:
        class LoginPage(BasePage): ...
        class DashboardPage(BasePage): ...

    Usage:
        page_obj = LoginPage(page)   # page is a Playwright Page instance from conftest.py
        page_obj.fill("#username", "user@example.com")
        page_obj.click("#submit")
    """

    def __init__(self, page: Page):
        """
        Args:
            page: Playwright Page object injected by the setup_browser fixture in conftest.py
        """
        self.page = page

    def wait_for_element(self, selector: str, timeout: int = 30000):
        """
        Wait for an element to appear in the DOM before interacting with it.

        Args:
            selector: CSS selector or XPath (e.g. "#username", "//span[@title='Home']")
            timeout:  Max wait time in milliseconds. Default is 30 seconds.

        Use this before interacting with elements that load asynchronously.
        Example:
            self.wait_for_element(".success-banner")
            self.wait_for_element("#dashboard", timeout=10000)
        """
        self.page.wait_for_selector(selector, timeout=timeout)

    def click(self, selector: str):
        """
        Click an element on the page.

        Args:
            selector: CSS selector or XPath of the element to click

        Example:
            self.click("#Login")
            self.click('button[type="submit"]')
        """
        self.page.click(selector)

    def fill(self, selector: str, value: str):
        """
        Clear an input field and type a value into it.

        Args:
            selector: CSS selector of the input field
            value:    Text to type into the field

        Example:
            self.fill("#username", "automation@renegadeinsurance.qa")
            self.fill('input[name="password"]', "MyPassword123")
        """
        self.page.fill(selector, value)

    def select_option(self, selector: str, value: str):
        """
        Select an option from a <select> dropdown by its value attribute.

        Args:
            selector: CSS selector of the <select> element
            value:    The value attribute of the <option> to select

        Example:
            self.select_option('select[name="state"]', "TX")
            self.select_option('select[name="coverageType"]', "Commercial Auto")
        """
        self.page.select_option(selector, value)

    def get_title(self):
        """
        Return the current page's <title> tag text.

        Returns:
            str: The page title

        Example:
            title = self.get_title()
            assert "Salesforce" in title
        """
        return self.page.title()

    def goto(self, url: str):
        """
        Navigate the browser to a URL.

        Args:
            url: Full URL to navigate to

        Example:
            self.goto("https://renegadeinsurancellc--qa.sandbox.lightning.force.com/")
        """
        self.page.goto(url)

    def is_visible(self, selector: str) -> bool:
        """
        Check if an element is visible on the page (returns True/False immediately).

        Args:
            selector: CSS selector or XPath of the element

        Returns:
            bool: True if visible, False if not present or hidden

        Example:
            if self.is_visible(".error-banner"):
                print("Error is showing")
        """
        return self.page.is_visible(selector)

    def get_text(self, selector: str) -> str:
        """
        Get the inner text content of an element.

        Args:
            selector: CSS selector of the element

        Returns:
            str: The visible text content of the element

        Example:
            message = self.get_text("div#error")
            assert "invalid credentials" in message
        """
        return self.page.inner_text(selector)
