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

import re
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

        Tries dialog-scoped click first (modal mode in My Agency app), then falls
        back to page-level click (full-page mode when opened via direct Account URL
        in a different app context, e.g. Logger Console).

        In full-page mode, clicking Next triggers URL navigation to
        Account/new?...&recordTypeId=... — wait for that navigation to settle
        rather than using a fixed timeout.

        Confirmed selector (Codegen):
            dialog.get_by_role("button", name="Next")
        """
        in_dialog = False
        try:
            dialog = self.page.get_by_role("dialog")
            dialog.get_by_role("button", name="Next").click()
            in_dialog = True
        except Exception:
            self.page.get_by_role("button", name="Next").click()

        if in_dialog:
            self.page.wait_for_timeout(1500)  # Form renders in-place within dialog
        else:
            # Full-page mode: Next navigates to Account/new?...&recordTypeId=...
            try:
                self.page.wait_for_url("**recordTypeId=*", timeout=10000)
                self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            except Exception:
                self.page.wait_for_timeout(1500)

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
        # ── Server Error recovery ─────────────────────────────────────────────
        # Salesforce sandboxes occasionally return a transient Server Error when
        # loading the account creation form. The URL already contains recordTypeId,
        # so reloading navigates directly to the correct form without re-selecting
        # the record type.
        if self.page.is_visible("text=Looks like there's a problem"):
            self.page.reload()
            self.page.wait_for_load_state("domcontentloaded", timeout=15000)
            self.page.wait_for_timeout(2000)

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
        # .nth(0) — two inputs share this name in the form; always target the first
        self.page.locator("input[name='VRNA__First_Name__c']").nth(0).fill(first_name)

        # ── Last Name ────────────────────────────────────────────────────────
        # .nth(0) — same reason as first name
        self.page.locator("input[name='VRNA__Last_Name__c']").nth(0).fill(last_name)

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

    def select_referral_source(self, value: str = None):
        """
        Select a value from the Referral Source combobox.

        Uses click → click (not select_option) because Referral Source is a
        Lightning (LWC) combobox, not a native <select> element.
        Confirmed selector via Playwright Codegen.

        Default behaviour (value=None): auto-selects the first available non-None,
        non-Other option by scoping to the combobox container. If this org only
        has '--None--' and 'Other', falls back to selecting 'Other' explicitly.

        'Other' triggers two required dependent fields: 'How did you learn about
        us?' and 'Other (Specify)'. These are ALWAYS filled after any selection —
        the 2-second wait silently passes when they are not present.

        Args:
            value: Referral source option label. If None, auto-selects first option.
        """
        combobox = self.page.get_by_role('combobox', name='Referral Source')
        combobox.click()

        if value:
            self.page.get_by_role('option', name=value).click()
        else:
            # Strategy 1: scope to the combobox container — avoids Target LOBs
            # dual-listbox options (which also have role="option").
            selected_non_other = False
            try:
                container = self.page.locator('.slds-combobox__container').filter(has=combobox)
                opt = container.get_by_role('option').filter(
                    has_not_text=re.compile(r'(--|other)', re.IGNORECASE)
                ).first
                opt.wait_for(timeout=3000)
                opt.click()
                selected_non_other = True
            except Exception:
                pass

            if not selected_non_other:
                # Strategy 2: org only has '--None--' and 'Other' — select Other
                # explicitly, then fill both dependent fields below.
                try:
                    self.page.get_by_role('option', name='Other').first.click(timeout=3000)
                except Exception:
                    # Last resort: any non-None option (closes the open dropdown)
                    try:
                        self.page.get_by_role('option').filter(
                            has_not_text='--None--'
                        ).first.click(timeout=3000)
                    except Exception:
                        pass

        # ── Dependent fields (only appear when 'Other' is selected) ──────────
        # A 2-second wait silently passes when these fields are not present.
        # When present, both are required and must be filled before save.
        try:
            how_combo = self.page.get_by_role('combobox', name='How did you learn about us?')
            how_combo.wait_for(timeout=2000)
            how_combo.click()
            # Scope to this combobox's container to avoid Target LOBs interference
            try:
                how_container = self.page.locator('.slds-combobox__container').filter(has=how_combo)
                how_opt = how_container.get_by_role('option').filter(has_not_text='--None--').first
                how_opt.wait_for(timeout=3000)
                how_opt.click()
            except Exception:
                # Fallback: page-level first non-None option (dropdown is open)
                self.page.get_by_role('option').filter(has_not_text='--None--').first.click(timeout=3000)
        except Exception:
            pass

        try:
            other_field = self.page.get_by_role('textbox', name='Other (Specify)')
            other_field.wait_for(timeout=2000)
            other_field.fill('Other')
        except Exception:
            pass

    # ── Save ────────────────────────────────────────────────────────────────

    def save(self):
        """
        Click Save and wait for Salesforce to navigate to the account detail page.

        wait_for_url("**/Account/**") would match the current URL immediately
        (Account/new?...&recordTypeId=...) and return without waiting for the
        actual post-save navigation. Use a lambda that only resolves when the URL
        moves to the account detail page (no 'new' or 'recordTypeId' in the path).

        Performs an early validation-error check 2 seconds after clicking Save so
        that form errors surface immediately rather than timing out after 30 s in
        wait_for_url and producing a confusing error location.
        """
        self.page.locator(self.save_button).click()
        # Short pause to let inline validation errors render before URL polling
        self.page.wait_for_timeout(2000)
        if self.is_save_error_visible():
            raise AssertionError(
                "Account save failed — validation errors are visible on the form. "
                "Check all required fields (Referral Source, dependent picklists, etc.)."
            )
        self.page.wait_for_url(
            lambda url: '/Account/' in url and 'new' not in url and 'recordTypeId' not in url,
            timeout=30000,
        )
        self.page.wait_for_load_state("domcontentloaded")

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
