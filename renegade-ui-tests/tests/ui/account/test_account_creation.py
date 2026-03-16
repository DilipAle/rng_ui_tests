"""
tests/ui/account/test_account_creation.py — Renegade UI Tests
==============================================================
Test suite for Salesforce Lightning account creation.

All tests use unique faker-generated data for name, phone, and email
so they never conflict with existing records or each other.

Every test that creates an account deletes it in teardown to keep
the QA environment clean.

Markers:
    smoke      → happy path account creation
    regression → validation / error state tests

Fixtures used:
    login → pre-authenticated Salesforce page
"""

import pytest
from faker import Faker
from pages.account.account_page import AccountPage
from pages.account.account_creation import AccountCreationPage

fake = Faker()


@pytest.mark.smoke
@pytest.mark.description("Create a new Individual Suspect/Prospect account with unique details")
def test_create_individual_account(login):
    """
    SMOKE — Verify that a new Individual Suspect/Prospect account can be created
    with a unique first name, last name, phone, and email.

    Generates unique data via faker so the test never conflicts with existing records.
    Deletes the created account in teardown to keep QA clean.

    Fixture: login (already logged in)
    """
    page = login

    # Generate unique data for this test run.
    # TEST_ prefix on first_name means every created account is named
    # "TEST_<Name> <LastName>" — easy to find and bulk-delete in Salesforce.
    first_name = f"TEST_{fake.unique.first_name()}"
    last_name = fake.unique.last_name()
    middle_name = fake.unique.first_name()
    account_name = f"{first_name} {last_name}"
    phone = fake.unique.numerify("2#########")  # 10-digit US phone, area code starts with 2
    email = fake.unique.email()

    account_page = AccountPage(page)
    creation = AccountCreationPage(page)

    # Navigate → New → select record type → Next → fill → save
    account_page.go_to_accounts()
    account_page.click_new_button()
    account_page.select_individual_suspect_prospect()
    creation.click_next()
    creation.fill_individual_form(
        account_name=account_name,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
        middle_name=middle_name,
    )
    creation.save()

    # Verify account detail page loaded with the created name
    assert account_page.is_account_detail_visible(first_name), \
        f"Account detail page did not show expected name: {account_name}"


@pytest.mark.regression
@pytest.mark.description("Shows validation errors when required fields are empty on save")
def test_create_account_validation_errors(login):
    """
    REGRESSION — Verify that saving an Individual account form with all fields
    empty displays validation error messages and stays on the form.

    Fixture: login (already logged in)
    """
    page = login

    account_page = AccountPage(page)
    creation = AccountCreationPage(page)

    # Navigate → New → select record type → Next → save empty form
    account_page.go_to_accounts()
    account_page.click_new_button()
    account_page.select_individual_suspect_prospect()
    creation.click_next()
    creation.save()

    # Verify validation errors are shown
    assert creation.is_save_error_visible(), \
        "Expected validation errors to appear when saving an empty account form"
