import pytest
from playwright.sync_api import sync_playwright
from pages.login.login_page import LoginPage
from config.config import Config  # Import the Config class
from config.browser_config import BrowserConfig  # Import the BrowserConfig class

@pytest.mark.smoke
@pytest.mark.description("Verify login with valid credentials")
def test_login_valid_credentials(login):
    """ Verify login with valid credentials """
    page = login

    # Wait for the page to load and verify login
    page.wait_for_selector("//span[@title = 'My Agency']", timeout=30000)  # waits for 30 seconds

    # Print the page title after login
    print(f"Page Title: {page.title()}")

@pytest.mark.regression
@pytest.mark.description("Verify login with invalid username")
def test_login_invalid_username(setup_browser, config):
    """ Verify login with invalid username """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials("invalid_user", config.PASSWORD)

    # Verify that the error message is shown 
    error_message = login_page.get_error_message()
    assert error_message == "Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator.", f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")

@pytest.mark.regression
@pytest.mark.description("Verify login with invalid password")
def test_login_invalid_password(setup_browser, config):
    """ Verify login with invalid password """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials(config.USERNAME, "invalid_pass")

    # Verify that the error message is shown
    error_message = login_page.get_error_message()
    assert error_message == "Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator.", f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")

   
@pytest.mark.regression
@pytest.mark.description("Verify login with empty password")
def test_login_empty_password(setup_browser, config):
    """ Verify login with empty password """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials(config.USERNAME, "")

    # Verify that the error message is shown
    error_message = login_page.get_error_message()
    assert error_message == "Error: Please enter your password.", f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")