"""
conftest.py — Customer Portal Tests
======================================
Pytest configuration loaded automatically before any test runs.
Defines shared fixtures for all Customer Portal UI tests.

Fixtures defined here:
    setup_browser → launches browser, yields page, closes after test
    config        → loads .env settings once per session
    login         → navigates to portal and logs in, yields authenticated page

Screenshot hook:
    pytest_runtest_makereport → captures full-page screenshot on test failure.
    Saved to: screenshots/<test_name>.png

Required .env file (place in customer-portal-tests/):
    ENV=qa
    QA_PORTAL_URL=https://...
    QA_PORTAL_USERNAME=your_username
    QA_PORTAL_PASSWORD=your_password
    BROWSER=chromium
    HEADLESS=true
"""

import sys
import os

# Add parent directory to sys.path so 'shared' package is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from config.config import Config
from config.browser_config import BrowserConfig
from pages.login.login_page import LoginPage


@pytest.fixture(scope="function")
def setup_browser():
    """
    Launch a browser and create a new page for each test.

    Scope: function — fresh browser per test.
    Viewport 1920x1080 ensures full page layout is visible.

    Yields:
        Page: Playwright Page object ready for interaction
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
    Load and return Customer Portal configuration from .env.

    Scope: session — loaded once and reused across all tests.

    Returns:
        Config: Configuration object (BASE_URL, USERNAME, PASSWORD, BROWSER, HEADLESS)
    """
    return Config()


@pytest.fixture(scope="function")
def login(setup_browser, config):
    """
    Log into the Customer Portal and return the authenticated page.

    Scope: function — login is performed fresh for every test.

    Yields:
        Page: Authenticated Playwright Page object (on dashboard or home)

    Use this in tests that require a logged-in state:
        def test_policies(login):
            page = login
            dashboard = DashboardPage(page)
            dashboard.go_to_policies()
    """
    page = setup_browser
    page.goto(config.BASE_URL)
    login_page = LoginPage(page)
    login_page.login(config.USERNAME, config.PASSWORD)
    yield page


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture a full-page screenshot when a test fails.

    Checks for 'login' fixture first, then falls back to 'setup_browser'.
    Screenshots saved to screenshots/<test_nodeid>.png
    Directory only created on first failure.
    """
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed:
        page = item.funcargs.get("login") or item.funcargs.get("setup_browser")
        if page:
            screenshot_dir = Path("screenshots")
            screenshot_dir.mkdir(exist_ok=True)
            test_name = item.nodeid.replace("/", "_").replace("::", "_").replace(" ", "_")
            try:
                page.screenshot(path=str(screenshot_dir / f"{test_name}.png"), full_page=True)
            except Exception:
                pass
