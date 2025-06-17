from playwright.sync_api import Page
from pages.base.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#Login"
        self.error_message_selector = "div#error"

    def login(self, username: str, password: str):
        """Performs login action"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def login_with_invalid_credentials(self, username: str, password: str):
        """Logs in with invalid credentials and checks for error message"""
        self.login(username, password)
        self.page.wait_for_selector(self.error_message_selector, timeout=30000)

    def is_logged_in(self):
        """Check if login was successful (you can customize the condition based on your app)"""
        return self.page.is_visible("//span[@title = 'My Agency']")

    def get_error_message(self):
        """Get the error message text from the page"""
        error_element = self.page.query_selector(self.error_message_selector)
        if error_element:
            return error_element.inner_text()
        else:
            return None

