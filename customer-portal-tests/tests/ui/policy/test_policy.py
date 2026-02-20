import pytest
from pages.dashboard.dashboard_page import DashboardPage
from pages.policy.policy_page import PolicyPage


@pytest.mark.smoke
@pytest.mark.description("Verify customer can view their policies")
def test_policy_list_visible(login):
    page = login
    dashboard = DashboardPage(page)
    dashboard.go_to_policies()

    policy_page = PolicyPage(page)
    assert policy_page.is_policy_list_visible(), "Policy list not visible"


@pytest.mark.regression
@pytest.mark.description("Verify policy list contains at least one policy")
def test_policy_list_not_empty(login):
    page = login
    dashboard = DashboardPage(page)
    dashboard.go_to_policies()

    policy_page = PolicyPage(page)
    count = policy_page.get_policy_count()
    assert count > 0, "Expected at least one policy in the list"
