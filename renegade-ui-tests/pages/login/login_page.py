"""
pages/login/login_page.py — Renegade UI Tests
===============================================
Page Object for the Salesforce Lightning login page.

Handles:
    - Standard username/password login
    - TOTP/MFA verification (auto-generates 6-digit code via pyotp)
    - Trusted IP bypass (TOTP skipped automatically when IP is whitelisted)
    - Invalid credential error message retrieval

Salesforce login page selectors:
    #username        → Username input field
    #password        → Password input field
    #Login           → Login button
    div#error        → Error message container
    input#tc         → TOTP 6-digit code input
    input#save       → TOTP verify button

MFA/TOTP Notes:
    - TOTP is only triggered if the login IP is NOT in Salesforce Trusted IP Ranges
    - To bypass TOTP locally: add your machine IP to Salesforce → Setup → Network Access
    - In CI/CD: add the GitHub Actions runner IP to Trusted IP Ranges
    - If TOTP is required: set QA_TOTP_SECRET in .env (base32 encoded secret)
    - Verify your secret works: python3 -c "import pyotp; print(pyotp.TOTP('SECRET').now())"
"""

from playwright.sync_api import Page
from pages.base.base_page import BasePage
import pyotp


class LoginPage(BasePage):
    """
    Page Object for Salesforce Lightning login page.

    Inherits all common browser actions from BasePage (click, fill, goto, etc.)

    Usage in conftest.py:
        login_page = LoginPage(page)
        login_page.login_with_totp(username, password, totp_secret)

    Usage in test (negative tests):
        login_page = LoginPage(page)
        login_page.login_with_invalid_credentials("wrong_user", "wrong_pass")
        error = login_page.get_error_message()
        assert "Please check your username" in error
    """

    def __init__(self, page):
        super().__init__(page)

        # Salesforce login page selectors
        self.username_input = "#username"
        self.password_input = "#password"
        self.login_button = "#Login"
        self.error_message_selector = "div#error"

        # TOTP/MFA verification page selectors
        self.totp_input = "input#tc"           # 6-digit code input field
        self.totp_verify_button = "input#save" # Verify / Submit button

    def login(self, username: str, password: str):
        """
        Fill in credentials and click the Login button.

        Does NOT handle TOTP — use login_with_totp() for full login flow.

        Args:
            username: Salesforce username (e.g. automation@renegadeinsurance.qa)
            password: Salesforce password
        """
        self.fill(self.username_input, username)
        self.fill(self.password_input, password)
        self.click(self.login_button)

    def handle_totp(self, totp_secret: str):
        """
        Detect and complete TOTP/MFA verification if the app redirects to it.

        Called automatically by login_with_totp() after credentials are submitted.
        If the page URL does NOT contain 'TotpVerificationUi', this method exits
        immediately (trusted IP scenario — no MFA needed).

        Args:
            totp_secret: Base32 TOTP secret key from .env (QA_TOTP_SECRET).
                         If empty or None, TOTP page is skipped silently.

        How TOTP works:
            - pyotp.TOTP(secret).now() generates the current 6-digit code
            - The same code is computed by the Salesforce authenticator app
            - Codes refresh every 30 seconds using the current timestamp + secret
        """
        try:
            # Only proceed if Salesforce redirected to the TOTP verification page.
            # Match broadly — Salesforce uses both "TotpVerificationUi" and
            # "TotpVerification" (without Ui) depending on org config and release.
            if "Totp" not in self.page.url and "totp" not in self.page.url.lower():
                return
            # If no secret is set, skip silently (cannot complete MFA)
            if not totp_secret:
                return
            # Generate the current 6-digit TOTP code right before entering it
            # to minimise the chance of the code expiring during slow page loads.
            self.page.wait_for_selector(self.totp_input, timeout=15000)
            code = pyotp.TOTP(totp_secret).now()
            self.page.fill(self.totp_input, code)
            self.page.click(self.totp_verify_button)
            # Wait for TOTP page to navigate away before returning
            self.page.wait_for_load_state("load", timeout=30000)
        except Exception:
            pass  # Never let MFA handling crash the test

    def login_with_totp(self, username: str, password: str, totp_secret: str):
        """
        Full login flow — credentials + automatic TOTP handling.

        This is the main login method used by the 'login' fixture in conftest.py.
        Steps:
            1. Fill username and password
            2. Click Login
            3. Wait for page to load
            4. Check if TOTP page appeared → if yes, complete MFA
            5. Return control to the test (now on the app homepage)

        Args:
            username:    Salesforce username
            password:    Salesforce password
            totp_secret: TOTP secret from .env (can be empty for Trusted IP setups)
        """
        self.login(username, password)
        self.page.wait_for_load_state("load")
        self.handle_totp(totp_secret)

    def login_with_invalid_credentials(self, username: str, password: str):
        """
        Submit invalid credentials and wait for the error message to appear.

        Used in negative test cases to verify Salesforce shows the correct error.

        Args:
            username: Any username (valid or invalid)
            password: Any password (valid or invalid, or empty string)
        """
        self.login(username, password)
        self.page.wait_for_selector(self.error_message_selector, timeout=30000)

    def is_logged_in(self):
        """
        Check if the current page shows a successful login state.

        Looks for the 'Home' navigation tab in the Salesforce navigation bar
        which only appears when the user is authenticated.

        Returns:
            bool: True if logged in, False otherwise
        """
        return self.page.is_visible(".slds-global-header")

    def get_error_message(self):
        """
        Read and return the error message text shown on login failure.

        Salesforce prepends 'Error: ' to all login error messages.
        Expected messages:
            "Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator."
            "Error: Please enter your password."

        Returns:
            str: The full error message text, or None if no error is shown
        """
        error_element = self.page.query_selector(self.error_message_selector)
        if error_element:
            return error_element.inner_text()
        else:
            return None
