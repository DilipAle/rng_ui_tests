from pages.base.base_page import BasePage


class SubmissionPage(BasePage):

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def start_new_submission(self):
        # TODO: implement
        pass

    def fill_account_info(self, data: dict):
        # TODO: implement
        pass

    def select_existing_account(self, account_name: str):
        # TODO: implement
        pass

    def click_next(self):
        # TODO: implement
        pass

    def click_save(self):
        # TODO: implement
        pass
