"""
shared/config.py
=================
Shared configuration class used by agency-height-tests and customer-portal-tests.

Reads all settings from the project's .env file using python-dotenv.
The renegade-ui-tests project has its own config/config.py with the same
pattern but different environment variable names (QA_URL vs QA_AH_URL etc.).

.env file must be placed in the root of the project that uses this config.
Never commit .env to git — it contains credentials.

Supported environments (set ENV= in .env):
    qa          → reads QA_* variables     (default)
    uat         → reads UAT_* variables
    production  → reads PROD_* variables

Switch environment at runtime:
    ENV=uat pytest -v
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Loads and exposes all test configuration from the .env file.

    Attributes:
        ENV (str):          Active environment — 'qa', 'uat', or 'production'
        BASE_URL (str):     The application URL for the active environment
        USERNAME (str):     Login username for the active environment
        PASSWORD (str):     Login password for the active environment
        TOTP_SECRET (str):  MFA secret key (optional — leave empty if using Trusted IP)
        BROWSER (str):      Browser to use — 'chromium', 'firefox', or 'webkit'
        HEADLESS (bool):    True = no browser window (CI/CD), False = visible browser (debugging)

    Usage in conftest.py:
        @pytest.fixture(scope="session")
        def config():
            return Config()

    Usage in test:
        def test_something(config):
            print(config.BASE_URL)
            print(config.USERNAME)
    """

    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()
        self.BASE_URL = self._get_base_url()
        self.USERNAME, self.PASSWORD, self.TOTP_SECRET = self._get_credentials()
        self.BROWSER = os.getenv("BROWSER", "chromium")

        # HEADLESS=true  → runs without a browser window (default, used in CI/CD)
        # HEADLESS=false → opens a visible browser window (useful for local debugging)
        self.HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    def _get_base_url(self):
        """
        Resolve the application URL based on the active environment.

        Returns:
            str: The base URL for the active environment

        Raises:
            ValueError: If ENV is set to an unsupported value
        """
        urls = {
            "production": os.getenv("PROD_URL"),
            "uat": os.getenv("UAT_URL"),
            "qa": os.getenv("QA_URL"),
        }
        if self.ENV not in urls:
            raise ValueError(f"Unsupported environment: {self.ENV}")
        return urls[self.ENV]

    def _get_credentials(self):
        """
        Load username, password and TOTP secret for the active environment.

        Returns:
            tuple: (username, password, totp_secret)

        Raises:
            ValueError: If username or password is missing from .env
        """
        prefix = self.ENV.upper()
        username = os.getenv(f"{prefix}_USERNAME")
        password = os.getenv(f"{prefix}_PASSWORD")
        totp_secret = os.getenv(f"{prefix}_TOTP_SECRET")  # Optional — can be empty

        if not username or not password:
            raise ValueError(f"Credentials for {self.ENV} environment are missing in .env")

        return username, password, totp_secret

    def get_browser_type(self):
        """
        Return the configured browser type string.

        Returns:
            str: 'chromium', 'firefox', or 'webkit'
        """
        return self.BROWSER

    def is_headless(self):
        """
        Return whether the browser should run in headless mode.

        Returns:
            bool: True if headless (no window), False if visible
        """
        return self.HEADLESS
