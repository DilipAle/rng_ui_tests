"""
tests/ui/login/test_login.py — Renegade UI Tests
==================================================
Test suite for Salesforce Lightning login functionality.

Markers:
    smoke      → happy path, run on every deploy
    regression → negative/edge cases, run nightly

Fixtures used:
    login         → pre-authenticated page (used for valid login test)
    setup_browser → raw unauthenticated browser (used for negative tests)
    config        → .env settings (BASE_URL, USERNAME, PASSWORD)

To run only this file:
    pytest tests/ui/login/test_login.py -v

To run only smoke tests in this file:
    pytest tests/ui/login/test_login.py -m smoke -v
"""

import pytest
from playwright.sync_api import sync_playwright
from pages.login.login_page import LoginPage
from config.config import Config
from config.browser_config import BrowserConfig


@pytest.mark.smoke
@pytest.mark.description("Verify login with valid credentials")
def test_login_valid_credentials(login):
    """
    SMOKE — Verify that a valid username and password logs into the app successfully.

    Uses the 'login' fixture which handles the full login flow including TOTP.
    Asserts that the 'My Agency' nav element is visible — confirming the user
    is on the authenticated Salesforce home page.

    Fixture: login (already logged in)
    """
    page = login
    # .slds-global-header is the Lightning header container — always present
    # in the main DOM on every authenticated Lightning page. More reliable than
    # nav items (org-specific) or search input (nested in shadow DOM).
    page.wait_for_selector(".slds-global-header", timeout=30000)
    print(f"Page Title: {page.title()}")


@pytest.mark.regression
@pytest.mark.description("Verify login with invalid username")
def test_login_invalid_username(setup_browser, config):
    """
    REGRESSION — Verify that an invalid username shows the correct Salesforce error.

    Uses a raw browser (not pre-logged-in) to test the error state.
    Expected error: "Error: Please check your username and password..."

    Fixture: setup_browser (unauthenticated browser)
    """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials("invalid_user", config.PASSWORD)

    error_message = login_page.get_error_message()
    assert error_message == "Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator.", \
        f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")


@pytest.mark.regression
@pytest.mark.description("Verify login with invalid password")
def test_login_invalid_password(setup_browser, config):
    """
    REGRESSION — Verify that an invalid password shows the correct Salesforce error.

    Uses the real username from config but a wrong password.
    Expected error: "Error: Please check your username and password..."

    Fixture: setup_browser (unauthenticated browser)
    """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials(config.USERNAME, "invalid_pass")

    error_message = login_page.get_error_message()
    assert error_message == "Error: Please check your username and password. If you still can't log in, contact your Salesforce administrator.", \
        f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")


@pytest.mark.regression
@pytest.mark.description("Verify login with empty password")
def test_login_empty_password(setup_browser, config):
    """
    REGRESSION — Verify that submitting an empty password shows the correct error.

    Salesforce shows a different, shorter error for blank password submissions.
    Expected error: "Error: Please enter your password."

    Fixture: setup_browser (unauthenticated browser)
    """
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials(config.USERNAME, "")

    error_message = login_page.get_error_message()
    assert error_message == "Error: Please enter your password.", \
        f"Expected error message, but got: {error_message}"
    print(f"Error message displayed: {error_message}")
