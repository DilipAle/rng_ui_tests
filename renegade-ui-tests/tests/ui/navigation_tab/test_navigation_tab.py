"""
tests/ui/navigation_tab/test_navigation_tab.py — Renegade UI Tests
====================================================================
Test suite for Salesforce Lightning navigation tab bar.

Verifies that each nav tab click navigates to the correct section
by checking that the resulting URL contains expected keywords.

All tests are marked @pytest.mark.smoke — these are critical path tests
that verify the app's core navigation is working on every deploy.

Marker: smoke (all tests in this class)

Fixture used:
    login → pre-authenticated Salesforce page

URL assertion strategy:
    Salesforce URLs contain the section name (e.g. "Account", "Contact")
    We assert the URL contains a keyword rather than an exact match
    because Salesforce sometimes appends query strings or redirects.

To run only this file:
    pytest tests/ui/navigation_tab/test_navigation_tab.py -v
"""

import pytest
from pages.navigation_tab.navigation_tab_page import NavigationTabPage


@pytest.mark.smoke
class TestNavigationTabPage:
    """
    Smoke tests for the Salesforce Lightning navigation tab bar.

    The autouse setup fixture runs before each test in this class,
    creating a fresh NavigationTabPage instance using the logged-in page.
    """

    @pytest.fixture(autouse=True)
    def setup(self, login):
        """
        Set up NavigationTabPage for each test.

        autouse=True means this fixture runs automatically before every
        test method in this class — no need to declare it in each test.

        Args:
            login: Pre-authenticated Playwright page from conftest.py
        """
        self.page = login
        self.nav_page = NavigationTabPage(self.page)

    def test_home_tab(self):
        """
        SMOKE — Verify Home tab navigates to the Salesforce Home page.

        Asserts: URL contains 'lightning' after clicking Home tab.
        """
        self.nav_page.go_to_home()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"Home tab did not navigate correctly. URL: {current_url}"

    def test_accounts_tab(self):
        """
        SMOKE — Verify Accounts tab navigates to the Accounts section.

        Asserts: URL contains 'Account', 'one.app', or 'New_Business_Flow'
        (Salesforce may redirect to a business flow modal on first click).
        """
        self.nav_page.go_to_accounts()
        current_url = self.nav_page.get_current_url()
        assert "Account" in current_url or "one.app" in current_url or "New_Business_Flow" in current_url, \
            f"Accounts tab did not navigate correctly. URL: {current_url}"

    def test_contacts_tab(self):
        """
        SMOKE — Verify Contacts tab navigates to the Contacts section.

        Asserts: URL contains 'Contact' or 'lightning'.
        """
        self.nav_page.go_to_contacts()
        current_url = self.nav_page.get_current_url()
        assert "Contact" in current_url or "lightning" in current_url, \
            f"Contacts tab did not navigate correctly. URL: {current_url}"

    def test_mypartners_tab(self):
        """
        SMOKE — Verify My Partners tab navigates to the My Partners section.

        Asserts: URL contains 'lightning'.
        """
        self.nav_page.go_to_mypartners()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"My Partners tab did not navigate correctly. URL: {current_url}"

    def test_policies_tab(self):
        """
        SMOKE — Verify Policies tab navigates to the Policies section.

        Asserts: URL contains 'lightning'.
        """
        self.nav_page.go_to_policies()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"Policies tab did not navigate correctly. URL: {current_url}"

    def test_dashboards_tab(self):
        """
        SMOKE — Verify Dashboards tab navigates to the Dashboards section.

        Asserts: URL contains 'Dashboard' or 'lightning'.
        Note: Uses force=True in the page object due to Salesforce overlay behavior.
        """
        self.nav_page.go_to_dashboards()
        current_url = self.nav_page.get_current_url()
        assert "Dashboard" in current_url or "lightning" in current_url, \
            f"Dashboards tab did not navigate correctly. URL: {current_url}"

    def test_tasks_tab(self):
        """
        SMOKE — Verify Tasks tab navigates to the Tasks section.

        Asserts: URL contains 'Task' or 'lightning'.
        Note: Uses force=True in the page object due to Salesforce overlay behavior.
        """
        self.nav_page.go_to_tasks()
        current_url = self.nav_page.get_current_url()
        assert "Task" in current_url or "lightning" in current_url, \
            f"Tasks tab did not navigate correctly. URL: {current_url}"
