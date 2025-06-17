# conftest.py
import pytest
from config.config import Config
from config.browser_config import BrowserConfig
from pages.login.login_page import LoginPage  # Fixed import statement for LoginPage
from playwright.sync_api import sync_playwright

# Fixture to set up browser and page for each test
@pytest.fixture(scope="function")
def setup_browser():
    """Fixture to set up browser and page for each test"""
    with sync_playwright() as playwright:
        browser_config = BrowserConfig(playwright)  # Pass playwright instance to BrowserConfig
        browser = browser_config.launch_browser()
        page = browser.new_page()
        yield page  # Provide the page to the test
        browser.close()  # Close the browser after the test is done

# Fixture to provide config dynamically to all tests
@pytest.fixture(scope="session")
def config():
    """Fixture to provide config dynamically to all tests"""
    return Config()


# Fixture for logging in
@pytest.fixture(scope="function")
def login(setup_browser, config):
    """Logs into the application and returns the page"""
    page = setup_browser  # Use the provided setup_browser fixture
    page.goto(config.BASE_URL)
    login_page = LoginPage(page)  # Create an instance of the LoginPage

    # Perform login using credentials from the config file
    login_page.login(config.USERNAME, config.PASSWORD)

    # Return the logged-in page
    yield page

    # Optionally, logout logic can go here if needed after the test
    # e.g., login_page.logout()
