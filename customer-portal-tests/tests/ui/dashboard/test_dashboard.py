import pytest
from pages.dashboard.dashboard_page import DashboardPage


@pytest.mark.smoke
@pytest.mark.description("Verify dashboard loads after login")
def test_dashboard_loads(login):
    page = login
    dashboard = DashboardPage(page)
    assert dashboard.is_loaded(), "Dashboard did not load after login"


@pytest.mark.regression
@pytest.mark.description("Verify dashboard navigation links are present")
def test_dashboard_navigation_visible(login):
    page = login
    dashboard = DashboardPage(page)
    assert page.is_visible(dashboard.nav_policies), "Policies nav link not visible"
    assert page.is_visible(dashboard.nav_billing), "Billing nav link not visible"
