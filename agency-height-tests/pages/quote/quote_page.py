from pages.base.base_page import BasePage


class QuotePage(BasePage):
    """
    Page Object for Agency Height quote review page.
    Update selectors to match the actual Agency Height UI.
    """

    def __init__(self, page):
        super().__init__(page)
        self.quote_list = ".quotes-table"
        self.quote_row = ".quote-row"
        self.quote_premium = ".quote-premium"
        self.quote_status = ".quote-status"
        self.bind_button = "button[data-action='bind-quote']"
        self.decline_button = "button[data-action='decline-quote']"

    def is_quote_list_visible(self) -> bool:
        return self.page.is_visible(self.quote_list)

    def get_quote_count(self) -> int:
        return len(self.page.query_selector_all(self.quote_row))

    def get_first_premium(self) -> str:
        el = self.page.query_selector(self.quote_premium)
        return el.inner_text() if el else None

    def bind_first_quote(self):
        self.click(self.bind_button)
        self.page.wait_for_load_state("networkidle")
