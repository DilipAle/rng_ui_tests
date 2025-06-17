import pytest
from pages.navigation_tab.navigation_tab_page import NavigationTabPage
from pages.base.base_page import BasePage
from pages.login.login_page import LoginPage
from config.config import Config 

@pytest.mark.smoke
@pytest.mark.description("Verify navigation bar tabs functionality")
class TestNavigationTabPage:
    
    def test_navigation_tabs(self, login, config):
        """Verify navigation by clicking through all tabs"""
        # Get the page from setup_browser
        page = login  # Use the page from the login fixture (this ensures user is logged in)

        # Test each tab's functionality in one go
        self.nav_page = NavigationTabPage(page)
        print(f"Current page URL: {page.url}")

        self.nav_page.go_to_home()

        self.nav_page.go_to_accounts()

        self.nav_page.go_to_contacts()

       
