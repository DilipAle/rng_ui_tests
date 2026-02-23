"""
conftest.py — Renegade UI Tests
=================================
Pytest configuration file loaded automatically before any test runs.
Defines shared fixtures available to all tests in this project.

Fixtures defined here:
    setup_browser  → launches browser, yields page, closes browser after test
    config         → loads .env settings once per session
    login          → navigates to app and logs in, yields authenticated page

Screenshot hook:
    pytest_runtest_makereport → captures a full-page screenshot when any test fails.
    Screenshots saved to: screenshots/<test_name>.png
    Only created on failure — directory is never created if all tests pass.

How fixtures are used in tests:
    def test_something(login):         # already logged in — use this for most tests
    def test_something(setup_browser): # raw browser — use this for login/error tests

Fixture scopes:
    session  → runs once per entire test session (e.g. config)
    function → runs once per test (e.g. setup_browser, login)
"""

import sys
import os

# Add the parent directory (AuotmationAuto360/) to sys.path so that
# 'shared' package is importable as: from shared.base_page import BasePage
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pathlib import Path
from config.config import Config
from config.browser_config import BrowserConfig
from pages.login.login_page import LoginPage
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="function")
def setup_browser():
    """
    Launch a browser and create a new page for each test.

    Scope: function — a fresh browser is launched for every single test.
    Viewport is set to 1920x1080 to ensure Salesforce nav tabs are fully visible.

    Yields:
        Page: A Playwright Page object ready for interaction

    Teardown:
        Browser is closed automatically after the test completes.

    Use this fixture directly in tests that do NOT require login:
        def test_login_error(setup_browser, config):
            page = setup_browser
            page.goto(config.BASE_URL)
    """
    with sync_playwright() as playwright:
        browser_config = BrowserConfig(playwright)
        browser = browser_config.launch_browser()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        yield page
        browser.close()


@pytest.fixture(scope="session")
def config():
    """
    Load and return application configuration from the .env file.

    Scope: session — runs once and is reused across all tests.
    Reads ENV, BASE_URL, USERNAME, PASSWORD, TOTP_SECRET, BROWSER, HEADLESS.

    Returns:
        Config: Configuration object with all settings

    Usage:
        def test_something(config):
            print(config.BASE_URL)
            print(config.USERNAME)
    """
    return Config()


@pytest.fixture(scope="function")
def login(setup_browser, config):
    """
    Log into the Renegade Insurance Salesforce app and return the authenticated page.

    Scope: function — login is performed fresh for every test that uses this fixture.
    Handles TOTP/MFA automatically if the app triggers it.
    If the machine IP is in Salesforce's Trusted IP range, TOTP is skipped silently.

    Depends on:
        setup_browser → provides the browser page
        config        → provides BASE_URL, USERNAME, PASSWORD, TOTP_SECRET

    Yields:
        Page: An authenticated Playwright Page object (already logged in)

    Use this fixture in tests that require an authenticated session:
        def test_navigation(login):
            page = login
            nav = NavigationTabPage(page)
            nav.go_to_accounts()
    """
    page = setup_browser
    page.goto(config.BASE_URL)
    login_page = LoginPage(page)

    # login_with_totp handles both regular login and MFA/TOTP verification
    login_page.login_with_totp(config.USERNAME, config.PASSWORD, config.TOTP_SECRET)

    # Wait for Salesforce home page to fully render before yielding to tests.
    # After TOTP redirect, Lightning takes extra time to load the nav bar.
    page.wait_for_selector("//span[@title='My Agency']", timeout=60000)

    yield page

    # Add logout logic here if needed between tests
    # e.g., login_page.logout()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Pytest hook that runs after each test phase (setup / call / teardown).

    When a test FAILS during the 'call' phase:
        1. Looks for a Playwright page object in the test's fixtures
           (checks 'login' fixture first, then 'setup_browser')
        2. Creates the screenshots/ directory if it doesn't exist
        3. Takes a full-page screenshot named after the test
        4. Screenshot path: screenshots/<test_nodeid>.png

    Screenshot filename example:
        tests_ui_login_test_login.py_test_login_valid_credentials.png

    Note:
        - screenshots/ directory is ONLY created when a test fails
        - screenshots/ is in .gitignore — never committed to git
        - Screenshots are uploaded as CI/CD artifacts for 7 days
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        # Try login fixture first (most tests), fall back to setup_browser
        page = item.funcargs.get("login") or item.funcargs.get("setup_browser")
        if page:
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            # Sanitize test node ID to use as filename
            test_name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
            try:
                page.screenshot(path=str(screenshot_dir / f"{test_name}.png"), full_page=True)
            except Exception:
                pass  # Never let screenshot failure break the test report
