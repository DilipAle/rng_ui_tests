import pytest
from pages.login.login_page import LoginPage


@pytest.mark.smoke
@pytest.mark.description("Verify customer can log in with valid credentials")
def test_login_valid_credentials(login):
    page = login
    assert "/dashboard" in page.url or "/home" in page.url, \
        f"Expected dashboard URL after login, got: {page.url}"


@pytest.mark.regression
@pytest.mark.description("Verify error shown on invalid credentials")
def test_login_invalid_credentials(setup_browser, config):
    page = setup_browser
    page.goto(config.BASE_URL)

    login_page = LoginPage(page)
    login_page.login_with_invalid_credentials("wrong@example.com", "wrongpass")

    error = login_page.get_error_message()
    assert error is not None, "Expected an error message, but none was displayed"
