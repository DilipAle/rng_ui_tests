import pytest
from pages.navigation_tab.navigation_tab_page import NavigationTabPage


@pytest.mark.smoke
class TestNavigationTabPage:

    @pytest.fixture(autouse=True)
    def setup(self, login):
        """Set up nav page for each test"""
        self.page = login
        self.nav_page = NavigationTabPage(self.page)

    def test_home_tab(self):
        """Verify Home tab navigates to Home page"""
        self.nav_page.go_to_home()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"Home tab did not navigate correctly. URL: {current_url}"

    def test_accounts_tab(self):
        """Verify Accounts tab navigates to Accounts page"""
        self.nav_page.go_to_accounts()
        current_url = self.nav_page.get_current_url()
        assert "Account" in current_url or "one.app" in current_url, \
            f"Accounts tab did not navigate correctly. URL: {current_url}"

    def test_contacts_tab(self):
        """Verify Contacts tab navigates to Contacts page"""
        self.nav_page.go_to_contacts()
        current_url = self.nav_page.get_current_url()
        assert "Contact" in current_url or "lightning" in current_url, \
            f"Contacts tab did not navigate correctly. URL: {current_url}"

    def test_mypartners_tab(self):
        """Verify My Partners tab navigates to My Partners page"""
        self.nav_page.go_to_mypartners()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"My Partners tab did not navigate correctly. URL: {current_url}"

    def test_policies_tab(self):
        """Verify Policies tab navigates to Policies page"""
        self.nav_page.go_to_policies()
        current_url = self.nav_page.get_current_url()
        assert "lightning" in current_url, \
            f"Policies tab did not navigate correctly. URL: {current_url}"

    def test_dashboards_tab(self):
        """Verify Dashboards tab navigates to Dashboards page"""
        self.nav_page.go_to_dashboards()
        current_url = self.nav_page.get_current_url()
        assert "Dashboard" in current_url or "lightning" in current_url, \
            f"Dashboards tab did not navigate correctly. URL: {current_url}"

    def test_tasks_tab(self):
        """Verify Tasks tab navigates to Tasks page"""
        self.nav_page.go_to_tasks()
        current_url = self.nav_page.get_current_url()
        assert "Task" in current_url or "lightning" in current_url, \
            f"Tasks tab did not navigate correctly. URL: {current_url}"
