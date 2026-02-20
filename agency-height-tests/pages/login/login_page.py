from pages.base.base_page import BasePage


class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Update selectors to match Agency Height's actual HTML
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']"
        self.error_message_selector = ".alert-error"

    def login(self, username: str, password: str):
        self.fill(self.email_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)
        self.page.wait_for_load_state("networkidle")

    def login_with_invalid_credentials(self, username: str, password: str):
        self.login(username, password)
        self.page.wait_for_selector(self.error_message_selector, timeout=15000)

    def get_error_message(self) -> str:
        el = self.page.query_selector(self.error_message_selector)
        return el.inner_text() if el else None

    def is_logged_in(self) -> bool:
        return "/dashboard" in self.page.url or "/submissions" in self.page.url
