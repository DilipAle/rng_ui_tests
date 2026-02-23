from pages.base.base_page import BasePage


class PolicyPage(BasePage):

    def __init__(self, page):
        super().__init__(page)
        self.page = page

    def add_policy(self, data: dict):
        # TODO: implement
        pass

    def move_to_stage(self, stage: str):
        # TODO: implement
        pass

    def move_to_sold(self):
        # TODO: implement
        pass

    def get_current_stage(self):
        # TODO: implement
        pass
