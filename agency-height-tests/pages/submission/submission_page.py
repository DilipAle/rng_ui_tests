from pages.base.base_page import BasePage


class SubmissionPage(BasePage):
    """
    Page Object for Agency Height submission creation flow.
    Update selectors to match the actual Agency Height UI.
    """

    def __init__(self, page):
        super().__init__(page)
        # Navigation
        self.new_submission_button = "button[data-action='new-submission']"
        self.submission_list = ".submissions-table"
        self.submission_row = ".submission-row"

        # Submission form fields
        self.insured_name_input = "input[name='insuredName']"
        self.insured_email_input = "input[name='insuredEmail']"
        self.coverage_type_select = "select[name='coverageType']"
        self.effective_date_input = "input[name='effectiveDate']"
        self.state_select = "select[name='state']"
        self.submit_button = "button[data-action='submit-submission']"

        # Confirmation
        self.success_banner = ".submission-success"
        self.submission_id_label = ".submission-id"

    def start_new_submission(self):
        self.click(self.new_submission_button)
        self.page.wait_for_load_state("networkidle")

    def fill_submission_form(self, insured_name: str, insured_email: str,
                             coverage_type: str, effective_date: str, state: str):
        self.fill(self.insured_name_input, insured_name)
        self.fill(self.insured_email_input, insured_email)
        self.select_option(self.coverage_type_select, coverage_type)
        self.fill(self.effective_date_input, effective_date)
        self.select_option(self.state_select, state)

    def submit(self):
        self.click(self.submit_button)
        self.page.wait_for_load_state("networkidle")

    def is_submission_successful(self) -> bool:
        return self.page.is_visible(self.success_banner)

    def get_submission_id(self) -> str:
        el = self.page.query_selector(self.submission_id_label)
        return el.inner_text() if el else None

    def get_submission_count(self) -> int:
        return len(self.page.query_selector_all(self.submission_row))
