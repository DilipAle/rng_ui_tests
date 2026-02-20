import pytest
from pages.submission.submission_page import SubmissionPage
from pages.quote.quote_page import QuotePage


@pytest.mark.smoke
@pytest.mark.description("Verify quotes appear after submission is processed")
def test_quotes_visible_after_submission(login):
    page = login
    quote_page = QuotePage(page)

    # Navigate to quotes (assumes submission already exists in test environment)
    page.goto(page.url.split("/")[0] + "/quotes")
    assert quote_page.is_quote_list_visible(), "Quote list is not visible"


@pytest.mark.regression
@pytest.mark.description("Verify quote has a premium value")
def test_quote_has_premium(login):
    page = login
    quote_page = QuotePage(page)

    page.goto(page.url.split("/")[0] + "/quotes")
    premium = quote_page.get_first_premium()
    assert premium is not None, "Expected a premium value on the first quote"
    print(f"First quote premium: {premium}")
