import os
from dotenv import load_dotenv

load_dotenv()


class SalesforceConfig:
    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()
        self.USERNAME = os.getenv(f"{self.ENV.upper()}_SF_USERNAME")
        self.PASSWORD = os.getenv(f"{self.ENV.upper()}_SF_PASSWORD")
        self.SECURITY_TOKEN = os.getenv(f"{self.ENV.upper()}_SF_SECURITY_TOKEN")
        self.DOMAIN = os.getenv(f"{self.ENV.upper()}_SF_DOMAIN", "test")  # 'test' for sandbox, 'login' for prod

        if not self.USERNAME or not self.PASSWORD:
            raise ValueError(f"Salesforce credentials for {self.ENV} are missing in .env")
