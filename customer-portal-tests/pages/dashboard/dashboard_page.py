from pages.base.base_page import BasePage


class DashboardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Update selectors to match actual Customer Portal HTML
        self.welcome_message = ".welcome-header"
        self.policy_summary_card = ".policy-summary"
        self.billing_summary_card = ".billing-summary"
        self.nav_policies = "a[href*='/policies']"
        self.nav_billing = "a[href*='/billing']"
        self.nav_profile = "a[href*='/profile']"
        self.logout_button = "button[data-action='logout']"

    def is_loaded(self) -> bool:
        return self.page.is_visible(self.welcome_message)

    def go_to_policies(self):
        self.click(self.nav_policies)
        self.page.wait_for_load_state("networkidle")

    def go_to_billing(self):
        self.click(self.nav_billing)
        self.page.wait_for_load_state("networkidle")

    def logout(self):
        self.click(self.logout_button)
        self.page.wait_for_load_state("networkidle")
