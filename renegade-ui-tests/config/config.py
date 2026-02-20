"""
config/config.py — Renegade UI Tests
======================================
Loads all test configuration from the .env file for the Renegade Insurance
Salesforce application.

Required .env variables:
    ENV=qa                          # qa | uat | production
    QA_URL=https://...              # Salesforce sandbox URL
    QA_USERNAME=automation@...      # Salesforce login username
    QA_PASSWORD=yourpassword        # Salesforce login password
    QA_TOTP_SECRET=                 # MFA secret — leave empty if using Trusted IP
    BROWSER=chromium                # chromium | firefox | webkit
    HEADLESS=true                   # true = no window | false = visible browser

To run against UAT instead of QA:
    ENV=uat pytest -v
    (requires UAT_URL, UAT_USERNAME, UAT_PASSWORD in .env)
"""

import os
from dotenv import load_dotenv

# Load variables from .env file in the project root
load_dotenv()


class Config:
    """
    Configuration for the Renegade UI test project.

    Attributes:
        ENV (str):          Active environment — 'qa', 'uat', or 'production'
        BASE_URL (str):     Salesforce URL for the active environment
        USERNAME (str):     Salesforce login username
        PASSWORD (str):     Salesforce login password
        TOTP_SECRET (str):  MFA/TOTP secret key (optional)
        BROWSER (str):      Browser to run tests in
        HEADLESS (bool):    True = headless mode, False = visible browser window

    Usage in conftest.py:
        @pytest.fixture(scope="session")
        def config():
            return Config()
    """

    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()
        self.BASE_URL = self.get_base_url()
        self.USERNAME, self.PASSWORD, self.TOTP_SECRET = self.get_credentials()
        self.BROWSER = os.getenv("BROWSER", "chromium")

        # HEADLESS=true  → no browser window (default, use in CI/CD)
        # HEADLESS=false → visible browser window (use for local debugging)
        self.HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    def get_base_url(self):
        """
        Resolve the Salesforce URL for the active environment.

        Returns:
            str: The base URL

        Raises:
            ValueError: If ENV is not qa, uat, or production
        """
        if self.ENV == "production":
            return os.getenv("PROD_URL")
        elif self.ENV == "uat":
            return os.getenv("UAT_URL")
        elif self.ENV == "qa":
            return os.getenv("QA_URL")
        else:
            raise ValueError(f"Unsupported environment: {self.ENV}")

    def get_credentials(self):
        """
        Load login credentials for the active environment.

        Returns:
            tuple: (username, password, totp_secret)
                   totp_secret may be None if not set in .env

        Raises:
            ValueError: If username or password is missing from .env
        """
        if self.ENV == "production":
            username = os.getenv("PROD_USERNAME")
            password = os.getenv("PROD_PASSWORD")
            totp_secret = os.getenv("PROD_TOTP_SECRET")
        elif self.ENV == "uat":
            username = os.getenv("UAT_USERNAME")
            password = os.getenv("UAT_PASSWORD")
            totp_secret = os.getenv("UAT_TOTP_SECRET")
        elif self.ENV == "qa":
            username = os.getenv("QA_USERNAME")
            password = os.getenv("QA_PASSWORD")
            totp_secret = os.getenv("QA_TOTP_SECRET")
        else:
            raise ValueError(f"Unsupported environment: {self.ENV}")

        if not username or not password:
            raise ValueError(f"Credentials for {self.ENV} environment are missing in the .env file")

        return username, password, totp_secret

    def get_browser_type(self):
        """Return the configured browser type string (chromium / firefox / webkit)."""
        return self.BROWSER

    def is_headless(self):
        """Return True if the browser should run without a visible window."""
        return self.HEADLESS
