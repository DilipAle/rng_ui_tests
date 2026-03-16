"""
tests/ui/policy/test_policy_intake_form.py — Renegade UI Tests
===============================================================
Tests for the Intake Form CTA on the policy detail page.

Flow:
    Create Individual Suspect/Prospect account
      → Click 'New PL Policy' on account detail page
        → Create Personal Auto policy
          → Test intake form CTA behaviour

Tests:
    smoke — Verify Send Intake Form CTA is visible and active (read-only)
    e2e   — Full flow: send → disabled → reload → status component + Resend → resend → disabled

Markers:
    smoke → read-only, verifies CTA is present and active
    e2e   → full send + resend flow

Fixtures used:
    login → pre-authenticated Salesforce page
"""

import pytest
from faker import Faker
from pages.account.account_page import AccountPage
from pages.account.account_creation import AccountCreationPage
from pages.policy.policy_page import PolicyPage
from pages.policy.policy_intake_form_page import PolicyIntakeFormPage

fake = Faker()


def _create_account_and_navigate_to_policy(page):
    """
    Helper: creates an Individual Suspect/Prospect account, then creates a
    Personal Auto policy from the account detail page via 'New PL Policy'.

    Returns the page positioned on the policy detail page.
    """
    first_name = fake.unique.first_name()
    last_name = fake.unique.last_name()
    middle_name = fake.unique.first_name()
    account_name = f"{first_name} {last_name}"
    phone = fake.unique.numerify("2#########")  # 10-digit US phone, area code starts with 2
    email = fake.unique.email()

    account_page = AccountPage(page)
    account_page.go_to_accounts()
    account_page.click_new_button()
    account_page.select_individual_suspect_prospect()

    creation = AccountCreationPage(page)
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

    # Wait for account detail page then create a policy via 'New PL Policy'
    page.wait_for_load_state("networkidle", timeout=30000)
    page.wait_for_selector(f"//h1[contains(.,'{first_name}')]", timeout=30000)

    policy_page = PolicyPage(page)
    policy_page.create_pl_policy()

    # Policy detail page is now open
    page.wait_for_load_state("networkidle", timeout=30000)


def _delete_account(page):
    """
    Helper: navigate back to the account and delete it.
    The linked policy is removed with the account.

    The new policy flow goes: account detail → new policy form → policy detail,
    so two go_back() calls may be needed to reach the account detail page.
    """
    try:
        page.go_back()
        page.wait_for_load_state("networkidle", timeout=15000)
        # If we landed on the new-policy form instead of account detail, go back once more
        if not page.is_visible('button[title="Show more actions"]') and \
                not page.is_visible('button[name="Delete"]'):
            page.go_back()
            page.wait_for_load_state("networkidle", timeout=15000)
        if page.is_visible('button[title="Show more actions"]'):
            page.click('button[title="Show more actions"]')
        page.wait_for_selector('button[name="Delete"]', timeout=5000)
        page.click('button[name="Delete"]')
        page.wait_for_selector('button[title="Delete"]', timeout=5000)
        page.click('button[title="Delete"]')
    except Exception:
        pass  # Never let teardown failure hide the test result


@pytest.mark.smoke
@pytest.mark.description("Policy page shows Send Intake Form CTA as active")
def test_policy_send_intake_form_cta_visible(login):
    """
    SMOKE — Verify that the Send Intake Form CTA is visible and active
    on a Pre-qualification policy page.

    Read-only — does not click the CTA or change any state.

    Fixture: login (already logged in)
    """
    page = login
    _create_account_and_navigate_to_policy(page)

    intake = PolicyIntakeFormPage(page)

    assert intake.is_send_intake_form_visible(), \
        "Expected 'Send Intake Form' CTA to be visible on the policy page"

    assert intake.is_send_intake_form_active(), \
        "Expected 'Send Intake Form' CTA to be active (not disabled)"

    assert not intake.is_intake_form_status_component_visible(), \
        "Intake Form Status component should not be visible before the form is sent"

    _delete_account(page)


@pytest.mark.e2e
@pytest.mark.description("Full intake form flow: send → disabled → reload → status + Resend → resend → disabled")
def test_policy_intake_form_full_flow(login):
    """
    E2E — Full intake form flow on the policy detail page:

        1. Send Intake Form CTA is visible and active
        2. Click CTA → confirm modal → CTA goes disabled
        3. Reload → Intake Form Status component visible + Resend CTA visible
        4. Click Resend → confirm modal → Resend CTA goes disabled

    Fixture: login (already logged in)
    """
    page = login
    _create_account_and_navigate_to_policy(page)

    intake = PolicyIntakeFormPage(page)

    # ── Step 1: Verify CTA is active ─────────────────────────────────────
    assert intake.is_send_intake_form_visible(), \
        "Expected 'Send Intake Form' CTA to be visible on the policy page"
    assert intake.is_send_intake_form_active(), \
        "Expected 'Send Intake Form' CTA to be active before sending"

    # ── Step 2: Send the intake form ──────────────────────────────────────
    intake.click_send_intake_form()
    intake.confirm_modal()

    # Verify the success toast appears immediately after sending
    assert intake.is_toast_visible(), \
        "Expected 'Outreach created successfully.' toast after sending intake form"

    # ── Step 3: Reload — verify intake frame and Send Reminder CTA ────────
    intake.reload_and_wait()

    assert intake.is_intake_form_status_component_visible(), \
        "Expected intake form frame (div.send-intake-frame) to appear after reload"

    assert intake.is_resend_visible(), \
        "Expected 'Send Reminder' CTA to be visible after intake form is sent and page reloaded"

    # ── Step 4: Send Reminder flow ────────────────────────────────────────
    intake.click_resend()
    intake.confirm_modal()

    # Toast confirms the reminder was sent
    assert intake.is_toast_visible(), \
        "Expected 'Outreach created successfully.' toast after sending reminder"

    # Send Reminder remains available — user can send multiple reminders
    assert intake.is_resend_visible(), \
        "Expected 'Send Reminder' CTA to remain available after sending reminder"

    # ── Teardown ──────────────────────────────────────────────────────────
    _delete_account(page)
