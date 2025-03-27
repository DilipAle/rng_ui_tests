import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    def __init__(self):
        self.ENV = os.getenv("ENV", "qa").lower()  # Default to 'qa'
        self.BASE_URL = self.get_base_url()
        self.USERNAME, self.PASSWORD = self.get_credentials()

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
        elif self.ENV == "uat":
            username = os.getenv("UAT_USERNAME")
            password = os.getenv("UAT_PASSWORD")
        elif self.ENV == "qa":
            username = os.getenv("QA_USERNAME")
            password = os.getenv("QA_PASSWORD")
        else:
            raise ValueError(f"Unsupported environment: {self.ENV}")
        
        if not username or not password:
            raise ValueError(f"Credentials for {self.ENV} environment are missing in the .env file")
        
        return username, password

# Example usage:
config = Config()
print(config.BASE_URL)
