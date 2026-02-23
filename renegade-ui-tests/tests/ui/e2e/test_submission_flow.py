import json
import pytest
import allure
from pathlib import Path
from pages.submission.submission_page import SubmissionPage
from pages.policy.policy_page import PolicyPage


def load_test_data(filename):
    data_path = Path(__file__).parent / "test_data" / filename
    with open(data_path) as f:
        return json.load(f)


@pytest.mark.e2e
@allure.epic("Renegade Insurance")
@allure.feature("Submission Flow")
class TestSubmissionFlow:

    @allure.title("Full submission flow - new account to sold")
    def test_submission_new_account_to_sold(self, login):
        page = login
        data = load_test_data("new_account.json")

        with allure.step("Start new submission"):
            submission = SubmissionPage(page)
            submission.start_new_submission()

        with allure.step("Fill account information"):
            submission.fill_account_info(data["account"])

        with allure.step("Add policy"):
            policy = PolicyPage(page)
            policy.add_policy(data["policy"])

        with allure.step("Move policy to sold"):
            policy.move_to_sold()

        with allure.step("Verify welcome email sent"):
            # TODO: implement email verification
            pass
