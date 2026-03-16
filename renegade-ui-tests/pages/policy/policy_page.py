"""
pages/policy/policy_page.py — Renegade UI Tests
=================================================
Page Object for policy creation from the account detail page.

All selectors confirmed against live QA via Playwright Codegen.

Flow:
    Account detail page
        → click 'New PL Policy' button
        → select Policy / Coverage Type from dropdown (--None-- → Personal Auto)
        → fill Effective Date and Expiration Date
        → click Save
        → verify toast message

Confirmed selectors:
    getByRole('button', name='New PL Policy')        → New PL Policy button
    locator('a').filter(has_text='--None--').first() → Coverage type dropdown
    getByRole('button', name='Personal Auto')        → Personal Auto option
    getByRole('textbox', name='Effective Date')      → Effective date field
    getByRole('textbox', name='Expiration Date')     → Expiration date field
    locator('span').filter(has_text='Save').first()  → Save button
"""

from pages.base.base_page import BasePage
from datetime import date, timedelta


class PolicyPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

    # ── New PL Policy ────────────────────────────────────────────────────────

    def click_new_pl_policy(self):
        """
        Click the 'New PL Policy' button on the account detail page.
        Confirmed selector: getByRole('button', name='New PL Policy')
        """
        self.page.get_by_role('button', name='New PL Policy').click()
        self.page.wait_for_load_state("load")

    def select_policy_coverage_type(self, coverage_type: str = 'Personal Auto'):
        """
        Select a coverage type from the Policy / Coverage Type dropdown.

        Steps:
            1. Click the --None-- anchor to open the dropdown
            2. Click the desired coverage type option

        Args:
            coverage_type: The coverage type to select (default: 'Personal Auto')

        Confirmed selectors:
            locator('a').filter(has_text='--None--').first()
            getByRole('button', name=coverage_type)
        """
        self.page.locator('a').filter(has_text='--None--').first().click()
        self.page.get_by_role('button', name=coverage_type).click()

    def fill_effective_date(self, effective_date: str):
        """
        Fill the Effective Date field.

        Args:
            effective_date: Date string in MM/DD/YYYY format (today or future)

        Confirmed selector: getByRole('textbox', name='Effective Date')
        """
        self.page.get_by_role('textbox', name='Effective Date').fill(effective_date)

    def fill_expiration_date(self, expiration_date: str):
        """
        Fill the Expiration Date field.

        Args:
            expiration_date: Date string in MM/DD/YYYY format (6 or 12 months from effective)

        Confirmed selector: getByRole('textbox', name='Expiration Date')
        """
        self.page.get_by_role('textbox', name='Expiration Date').fill(expiration_date)

    def save_policy(self):
        """
        Click Save to create the policy.
        Confirmed selector: locator('span').filter(has_text='Save').first()
        """
        self.page.locator('span').filter(has_text='Save').first().click()
        self.page.wait_for_load_state("load")

    # ── Full policy creation in one call ─────────────────────────────────────

    def create_pl_policy(
        self,
        coverage_type: str = 'Personal Auto',
        effective_date: str = None,
        expiration_date: str = None,
    ):
        """
        Complete the full New PL Policy creation flow from the account detail page.

        Args:
            coverage_type:   Coverage type (default: 'Personal Auto')
            effective_date:  MM/DD/YYYY — defaults to today
            expiration_date: MM/DD/YYYY — defaults to 1 year from today

        Usage:
            policy = PolicyPage(page)
            policy.create_pl_policy()
        """
        if effective_date is None:
            effective_date = date.today().strftime("%m/%d/%Y")
        if expiration_date is None:
            expiration_date = (date.today() + timedelta(days=365)).strftime("%m/%d/%Y")

        self.click_new_pl_policy()
        self.select_policy_coverage_type(coverage_type)
        self.fill_effective_date(effective_date)
        self.fill_expiration_date(expiration_date)
        self.save_policy()

    # ── Verification ─────────────────────────────────────────────────────────

    def is_policy_created_toast_visible(self) -> bool:
        """Returns True if a policy creation success toast is visible."""
        return (
            self.is_visible('span:has-text("was created")')
            or self.is_visible('[class*="toastMessage"]:has-text("created")')
        )

    # ── Legacy stubs (used by e2e submission test) ───────────────────────────

    def add_policy(self, data: dict):
        # TODO: implement with confirmed selectors when submission flow is built
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
