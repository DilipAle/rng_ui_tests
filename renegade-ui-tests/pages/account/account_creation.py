"""
pages/account/account_creation.py — Renegade UI Tests
=======================================================
Page Object for the Salesforce account creation form.

All selectors confirmed against live QA via Playwright Codegen.

Confirmed selectors:
    span.filter(hasText='Next').last()          → Next button label span (confirmed Codegen)
    input[name='Name']                          → Account/Customer Name (SF API name — most stable)
    getByRole('textbox', name='Customer Name')  → Account Name (visible label in this org)
    input[name='VRNA__First_Name__c']           → First Name (SF API name)
    input[name='VRNA__Last_Name__c']            → Last Name (SF API name)
    getByRole('textbox', name='Middle Name')    → Middle Name
    getByRole('textbox', name='Email')          → Email
    input[name="Phone"]                         → Phone
    getByRole('combobox', name='Referral Source') → Referral Source dropdown
    getByLabel('Address Search', exact=True)    → Address search field
    button[name="SaveEdit"]                     → Save button
    span:has-text("Account ... was created.")   → Success toast

Note: The visible label for the account name field is "Customer Name" in this org,
not "Account Name". Use input[name='Name'] (Salesforce API name) as the primary
selector — it is independent of the displayed label and survives label changes.
"""

from pages.base.base_page import BasePage
from faker import Faker

fake = Faker()


class AccountCreationPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Save button — confirmed via Codegen
        self.save_button = 'button[name="SaveEdit"]'

        # Phone — confirmed via Codegen (input[name] is stable)
        self.phone_input = 'input[name="Phone"]'

    # ── Navigation ──────────────────────────────────────────────────────────

    def click_next(self):
        """
        Click the Next button on the record type selection modal.

        Scoped to the dialog so it cannot match any other Next button on the page.
        wait_for_timeout(1500) after click lets the new-account form fully render
        before the test proceeds to fill fields.

        Confirmed selector (Codegen):
            dialog.get_by_role("button", name="Next")
        """
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_role("button", name="Next").click()
        self.page.wait_for_timeout(1500)  # Wait for new-account form to render

    # ── Form fill ───────────────────────────────────────────────────────────

    def fill_individual_form(
        self,
        account_name: str,
        first_name: str,
        last_name: str,
        phone: str,
        email: str,
        middle_name: str = None,
    ):
        """
        Fill in the Individual account creation form.

        Args:
            account_name: Full account name (required field)
            first_name:   First name (required field)
            last_name:    Last name (required field)
            phone:        Phone number
            email:        Email address
            middle_name:  Middle name (optional)

        Selector strategy — account name:
            1. input[name='Name']         — Salesforce API name (stable, label-independent)
            2. 'Customer Name'            — visible label in this org
            3. '*Account Name'            — label with required asterisk prefix
            4. 'Account Name'             — label without asterisk

        Selector strategy — first / last name:
            1. input[name='VRNA__First_Name__c'] / input[name='VRNA__Last_Name__c']
               — managed-package API names (stable)
            2. '*First Name' / '*Last Name'  — labels with required asterisk prefix
            3. 'First Name'  / 'Last Name'   — labels without asterisk
        """
        # ── Account / Customer Name ──────────────────────────────────────────
        for _loc in [
            lambda: self.page.locator("input[name='Name']"),
            lambda: self.page.get_by_role('textbox', name='Customer Name'),
            lambda: self.page.get_by_role('textbox', name='*Account Name'),
            lambda: self.page.get_by_role('textbox', name='Account Name'),
        ]:
            try:
                _el = _loc()
                _el.wait_for(timeout=3000)
                _el.fill(account_name)
                break
            except Exception:
                pass

        # ── First Name ───────────────────────────────────────────────────────
        for _loc in [
            lambda: self.page.locator("input[name='VRNA__First_Name__c']"),
            lambda: self.page.get_by_role('textbox', name='*First Name'),
            lambda: self.page.get_by_role('textbox', name='First Name'),
        ]:
            try:
                _el = _loc()
                _el.wait_for(timeout=2000)
                _el.fill(first_name)
                break
            except Exception:
                pass

        # ── Last Name ────────────────────────────────────────────────────────
        for _loc in [
            lambda: self.page.locator("input[name='VRNA__Last_Name__c']"),
            lambda: self.page.get_by_role('textbox', name='*Last Name'),
            lambda: self.page.get_by_role('textbox', name='Last Name'),
        ]:
            try:
                _el = _loc()
                _el.wait_for(timeout=2000)
                _el.fill(last_name)
                break
            except Exception:
                pass

        # ── Referral Source ──────────────────────────────────────────────────
        # Required field — must be filled before save or Salesforce returns a validation error
        self.select_referral_source()

        self.page.locator(self.phone_input).fill(phone)
        self.page.get_by_role('textbox', name='Email').fill(email)
        if middle_name:
            # API name confirmed from DOM: VRNA__Middle_Name__c
            # .first — two inputs share this name (Salesforce renders billing + physical sections)
            self.page.locator("input[name='VRNA__Middle_Name__c']").first.fill(middle_name)

    def fill_address(self, address: str):
        """
        Fill the Address Search field.

        Args:
            address: Street address to search (e.g. "123 Main St, Austin TX")
        """
        self.page.get_by_label('Address Search', exact=True).fill(address)

    def select_referral_source(self, value: str = 'Other'):
        """
        Select a value from the Referral Source combobox.

        Uses click → click (not select_option) because Referral Source is a
        Lightning (LWC) combobox, not a native <select> element.
        Confirmed selector via Playwright Codegen.

        Args:
            value: Referral source option label (default: 'Other')
        """
        self.page.get_by_role('combobox', name='Referral Source').click()
        self.page.get_by_role('option', name=value).click()

    # ── Save ────────────────────────────────────────────────────────────────

    def save(self):
        """Click Save and wait for the page to load."""
        self.page.locator(self.save_button).click()
        self.page.wait_for_load_state("load")

    # ── Verification ────────────────────────────────────────────────────────

    def is_account_created_toast_visible(self, account_name: str) -> bool:
        """
        Returns True if the account creation success toast is visible.

        Args:
            account_name: The account name that was just created
        """
        return self.is_visible(f'span:has-text("Account \\"{account_name}\\" was created.")')

    def is_save_error_visible(self) -> bool:
        """Returns True if any validation error is visible after a failed save."""
        return (
            self.is_visible(".forceFormValidationHelpText")
            or self.is_visible("[class*='errorContainer']")
            or self.is_visible(".slds-has-error")
        )
