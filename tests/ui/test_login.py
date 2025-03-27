from playwright.sync_api import sync_playwright
from pages.login_page import LoginPage
from config.config import Config  # Import the Config class

def test_login():
    # Get the configuration (environment details)
    config = Config()

    with sync_playwright() as playwright:
        # Launch the browser
        browser = playwright.chromium.launch(executable_path='./playwright_browsers/chromium-1055/chrome-mac/Chromium.app/Contents/MacOS/Chromium', headless=False)
        page = browser.new_page()

        # Navigate to the environment-specific URL
        page.goto(config.BASE_URL)

        # Create an instance of LoginPage
        login_page = LoginPage(page)

        # Perform login using credentials from the configuration
        login_page.login(config.USERNAME, config.PASSWORD)

        # Validate that the login was successful (assert page title or any other element)
        assert "Dashboard" in page.title(), "Login failed!"

        # Close the browser
        browser.close()

# Run the test
test_login()
