import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()  # Default to 'qa'
        self.BASE_URL = self.get_base_url()
        self.USERNAME, self.PASSWORD, self.TOTP_SECRET = self.get_credentials()
        self.BROWSER = os.getenv("BROWSER", "chromium")  # Default browser is chromium
        self.HEADLESS = os.getenv("HEADLESS", "true") == "false"

    def get_base_url(self):
        if self.ENV == "production":
            return os.getenv("PROD_URL")
        elif self.ENV == "uat":
            return os.getenv("UAT_URL")
        elif self.ENV == "qa":
            return os.getenv("QA_URL")
        else:
            raise ValueError(f"Unsupported environment: {self.ENV}")

    def get_credentials(self):
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
        """Helper method to get the browser type (chromium, firefox, or webkit)"""
        return self.BROWSER

    def is_headless(self):
        """Helper method to check if the browser should be in headless mode"""
        return self.HEADLESS

