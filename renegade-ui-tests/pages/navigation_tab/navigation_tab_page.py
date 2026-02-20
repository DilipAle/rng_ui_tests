"""
pages/navigation_tab/navigation_tab_page.py — Renegade UI Tests
=================================================================
Page Object for the Salesforce Lightning navigation tab bar.

The navigation bar appears at the top of the Salesforce app after login
and contains tabs: Home, Accounts, Contacts, My Partners, Policies,
Dashboards, Tasks.

Important: Viewport must be 1920x1080 (set in conftest.py setup_browser)
to ensure all tabs are visible. At 1280px default width, some tabs
are hidden in an overflow menu and clicks fail.

Selector pattern: a[title="TabName"]
    Salesforce renders nav tabs as anchor tags with a title attribute.

Note on force=True:
    Dashboards and Tasks tabs sometimes have a Salesforce overlay covering
    them briefly after navigation. force=True bypasses the visibility check
    and clicks even if an overlay is present.
"""

from pages.base.base_page import BasePage


class NavigationTabPage(BasePage):
    """
    Page Object for Salesforce Lightning navigation tab bar.

    Inherits all browser actions from BasePage.

    Usage in tests:
        nav = NavigationTabPage(page)
        nav.go_to_accounts()
        assert "Account" in nav.get_current_url()
    """

    # Navigation tab selectors — Salesforce uses a[title="..."] for nav tabs
    home_tab = 'a[title="Home"]'
    accounts_tab = 'a[title="Accounts"]'
    contacts_tab = 'a[title="Contacts"]'
    mypartners_tab = 'a[title="My Partners"]'
    policies_tab = 'a[title="Policies"]'
    dashboards_tab = 'a[title="Dashboards"]'
    tasks_tab = 'a[title="Tasks"]'

    def get_current_url(self):
        """
        Return the current browser URL.

        Used in tests to verify that clicking a tab navigated correctly.

        Returns:
            str: Full URL of the current page
        """
        return self.page.url

    def go_to_home(self):
        """Click the Home tab and wait for the page to fully load."""
        self.click(self.home_tab)
        self.page.wait_for_load_state("load")

    def go_to_accounts(self):
        """Click the Accounts tab and wait for the page to fully load."""
        self.click(self.accounts_tab)
        self.page.wait_for_load_state("load")

    def go_to_contacts(self):
        """Click the Contacts tab and wait for the page to fully load."""
        self.click(self.contacts_tab)
        self.page.wait_for_load_state("load")

    def go_to_mypartners(self):
        """Click the My Partners tab and wait for the page to fully load."""
        self.click(self.mypartners_tab)
        self.page.wait_for_load_state("load")

    def go_to_policies(self):
        """Click the Policies tab and wait for the page to fully load."""
        self.click(self.policies_tab)
        self.page.wait_for_load_state("load")

    def go_to_dashboards(self):
        """
        Click the Dashboards tab using force=True and wait for load.

        force=True is used here because Salesforce sometimes renders a
        brief overlay after navigation that covers this tab.
        """
        self.page.locator(self.dashboards_tab).click(force=True)
        self.page.wait_for_load_state("load")

    def go_to_tasks(self):
        """
        Click the Tasks tab using force=True and wait for load.

        force=True is used here because Salesforce sometimes renders a
        brief overlay after navigation that covers this tab.
        """
        self.page.locator(self.tasks_tab).click(force=True)
        self.page.wait_for_load_state("load")
