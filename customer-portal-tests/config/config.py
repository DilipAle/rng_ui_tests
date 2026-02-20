import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()
        self.BASE_URL = self._get_base_url()
        self.USERNAME, self.PASSWORD = self._get_credentials()
        self.BROWSER = os.getenv("BROWSER", "chromium")
        self.HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

    def _get_base_url(self):
        urls = {
            "production": os.getenv("PROD_PORTAL_URL"),
            "uat": os.getenv("UAT_PORTAL_URL"),
            "qa": os.getenv("QA_PORTAL_URL"),
        }
        if self.ENV not in urls:
            raise ValueError(f"Unsupported environment: {self.ENV}")
        return urls[self.ENV]

    def _get_credentials(self):
        prefix = self.ENV.upper()
        username = os.getenv(f"{prefix}_PORTAL_USERNAME")
        password = os.getenv(f"{prefix}_PORTAL_PASSWORD")

        if not username or not password:
            raise ValueError(f"Portal credentials for {self.ENV} are missing in .env")

        return username, password

    def get_browser_type(self):
        return self.BROWSER

    def is_headless(self):
        return self.HEADLESS
