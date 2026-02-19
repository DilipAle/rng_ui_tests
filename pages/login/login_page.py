from playwright.sync_api import Page
from pages.base.base_page import BasePage
import pyotp


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#Login"
        self.error_message_selector = "div#error"
        self.totp_input = "input#tc"
        self.totp_verify_button = "input#save"

    def login(self, username: str, password: str):
        """Performs login action"""
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def handle_totp(self, totp_secret: str):
        """Detects and handles TOTP verification page if it appears"""
        try:
            if "TotpVerificationUi" not in self.page.url:
                return
            if not totp_secret:
                return
            code = pyotp.TOTP(totp_secret).now()
            self.page.wait_for_selector(self.totp_input, timeout=10000)
            self.page.fill(self.totp_input, code)
            self.page.click(self.totp_verify_button)
        except Exception:
            pass

    def login_with_totp(self, username: str, password: str, totp_secret: str):
        """Performs login and handles TOTP verification if triggered"""
        self.login(username, password)
        self.page.wait_for_load_state("load")
        self.handle_totp(totp_secret)

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

