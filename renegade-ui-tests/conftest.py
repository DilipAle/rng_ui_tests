"""
conftest.py — Renegade UI Tests
=================================
Pytest configuration file loaded automatically before any test runs.

Auth strategy — session-scoped browser context + captured Lightning URL:
    Salesforce binds sessions to the browser instance. Storage-state (cookies
    in a file) does not work because Salesforce rejects the session on a new
    browser context.

    Instead we:
        1. Keep ONE playwright instance, browser, and context alive all session
        2. Log in + handle TOTP once in _auth_session
        3. Capture the Lightning URL that Salesforce lands on after login
        4. Each 'login' fixture opens a new page and navigates to that
           Lightning URL directly — no redirect through the login page,
           no credential/TOTP entry needed

Fixtures:
    setup_browser  → independent browser per test (for login/error tests)
    config         → loads .env settings once per session
    _playwright    → single Playwright instance for the whole session
    _browser       → single browser for the whole session
    _auth_session  → logs in once, holds context + home URL for all tests
    login          → fresh page per test inside the shared auth session

Screenshot hook:
    pytest_runtest_makereport → full-page screenshot on any test failure
    Saved to: screenshots/<test_name>.png
"""

import sys
import os
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pathlib import Path
from config.config import Config
from config.browser_config import BrowserConfig
from pages.login.login_page import LoginPage
from playwright.sync_api import sync_playwright


# ── Data class to bundle context + home URL ──────────────────────────────────

@dataclass
class AuthSession:
    context: object   # Playwright BrowserContext — stays alive all session
    home_url: str     # Lightning URL captured right after login


# ── Independent browser (for login / error tests) ────────────────────────────

@pytest.fixture(scope="function")
def setup_browser(_playwright):
    """
    Fresh browser + page per test.
    Use only for tests that do NOT need a logged-in session.
    Uses the session-scoped _playwright instance to avoid asyncio loop conflicts.
    """
    browser_config = BrowserConfig(_playwright)
    browser = browser_config.launch_browser()
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    yield page
    browser.close()


# ── Config ───────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def config():
    """Load .env config once for the whole session."""
    return Config()


# ── Session-scoped Playwright + browser ──────────────────────────────────────

@pytest.fixture(scope="session")
def _playwright():
    """Single Playwright instance for the entire test session."""
    p = sync_playwright().start()
    yield p
    p.stop()


@pytest.fixture(scope="session")
def _browser(_playwright):
    """Single browser instance for the entire test session."""
    browser_config = BrowserConfig(_playwright)
    browser = browser_config.launch_browser()
    yield browser
    browser.close()


# ── Login once, capture Lightning home URL ───────────────────────────────────

@pytest.fixture(scope="session")
def _auth_session(_browser, config):
    """
    Log in to Salesforce once and capture the Lightning URL that the app
    lands on after successful login.

    Why we capture the URL:
        config.BASE_URL is the classic Salesforce login domain
        (*.my.salesforce.com). After login, Salesforce redirects to the
        Lightning domain (*.lightning.force.com). If subsequent pages
        navigate back to the login domain, Salesforce may redirect through
        the auth flow again instead of silently resuming the session.
        Navigating directly to the captured Lightning URL skips that
        redirect entirely.

    Yields:
        AuthSession(context, home_url)
    """
    context = _browser.new_context(viewport={"width": 1920, "height": 1080})
    page = context.new_page()

    page.goto(config.BASE_URL)
    login_page = LoginPage(page)
    login_page.login_with_totp(config.USERNAME, config.PASSWORD, config.TOTP_SECRET)

    # Salesforce goes through a multi-step redirect chain after login:
    #   contentDoor → one.app → /lightning → /lightning/r/<object>/...
    # wait_for_url() misses already-completed redirects, so we poll instead.
    for _ in range(120):
        if "lightning.force.com" in page.url:
            break
        page.wait_for_timeout(1000)
    else:
        raise Exception(f"Login did not reach Lightning domain. Current URL: {page.url}")

    # Salesforce server-side session memory redirects to the last visited page
    # after login (e.g. a Log__c audit record from a previous test run). Navigate
    # to the Accounts list explicitly to establish a stable, app-neutral home URL
    # that every test can reliably navigate from without being redirected elsewhere.
    lightning_base = page.url.split('/lightning/')[0]
    page.goto(f"{lightning_base}/lightning/o/Account/list")
    for _ in range(30):
        if "/o/Account/" in page.url:
            break
        page.wait_for_timeout(1000)
    page.wait_for_load_state("domcontentloaded")

    # Capture the Account list URL — stable, no last-visited-page redirects
    home_url = page.url

    # Close the setup page — the context and its session stay alive
    page.close()

    yield AuthSession(context=context, home_url=home_url)

    context.close()


# ── Per-test login fixture ────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def login(_auth_session):
    """
    Open a fresh page in the shared authenticated context and navigate
    directly to the captured Lightning home URL.

    No login page, no username/password, no TOTP — the browser context
    is already authenticated from _auth_session.

    Scope: function — each test gets its own page, closed after the test.

    Yields:
        Page: An authenticated Playwright Page object
    """
    page = _auth_session.context.new_page()
    page.goto(_auth_session.home_url)

    # Confirm Lightning is still active — shared context keeps session alive
    for _ in range(60):
        if "lightning.force.com" in page.url:
            break
        page.wait_for_timeout(1000)
    else:
        raise Exception(f"Login fixture: not on Lightning domain. URL: {page.url}")

    yield page

    page.close()


# ── Screenshot on failure ─────────────────────────────────────────────────────

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture a full-page screenshot when a test fails."""
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
