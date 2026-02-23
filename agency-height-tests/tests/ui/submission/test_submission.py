import pytest
from pages.submission.submission_page import SubmissionPage


@pytest.mark.smoke
@pytest.mark.description("Verify agency can create a new submission")
def test_create_new_submission(login):
    page = login
    submission = SubmissionPage(page)

    submission.start_new_submission()
    submission.fill_submission_form(
        insured_name="Test Insured LLC",
        insured_email="insured@test.com",
        coverage_type="Commercial Auto",
        effective_date="03/01/2026",
        state="TX",
    )
    submission.submit()

    assert submission.is_submission_successful(), "Submission did not complete successfully"
    submission_id = submission.get_submission_id()
    assert submission_id, "No submission ID returned after submission"
    print(f"Created submission ID: {submission_id}")


@pytest.mark.regression
@pytest.mark.description("Verify submission list is visible after login")
def test_submission_list_visible(login):
    page = login
    submission = SubmissionPage(page)
    assert page.is_visible(submission.submission_list), "Submission list not visible"


@pytest.mark.regression
@pytest.mark.description("Verify required fields are validated on submission form")
def test_submission_form_required_fields(login):
    page = login
    submission = SubmissionPage(page)

    submission.start_new_submission()
    # Submit empty form — expect validation errors
    submission.submit()

    # At least one field error should be visible
    assert page.is_visible(".field-error") or page.is_visible(".validation-message"), \
        "Expected form validation errors but none appeared"
