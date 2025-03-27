from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Define the selectors for username, password, and login button
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#Login"

    def login(self, username: str, password: str):
        # Fill the username and password fields
        self.page.fill(self.username_input, username)
        self.page.fill(self.password_input, password)
        self.page.click(self.login_button)

    def get_title(self):
        return self.page.title()
