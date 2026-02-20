from pages.base.base_page import BasePage


class PolicyPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        # Update selectors to match actual Customer Portal HTML
        self.policy_list = ".policy-list"
        self.policy_row = ".policy-item"
        self.policy_number = ".policy-number"
        self.policy_status = ".policy-status"
        self.download_button = "button[data-action='download']"

    def get_policy_count(self) -> int:
        return len(self.page.query_selector_all(self.policy_row))

    def get_first_policy_number(self) -> str:
        el = self.page.query_selector(self.policy_number)
        return el.inner_text() if el else None

    def is_policy_list_visible(self) -> bool:
        return self.page.is_visible(self.policy_list)

    def download_first_policy(self):
        self.click(self.download_button)
