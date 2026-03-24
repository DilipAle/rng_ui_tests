"""
pages/account/account_page.py — Renegade UI Tests
===================================================
Page Object for the Salesforce Accounts list page.

All selectors confirmed against live QA via Playwright Codegen.

Confirmed selectors (Playwright Codegen):
    get_by_role("link", name="Accounts")                         → Accounts nav tab
    wait_for_url("**/o/Account/**")                              → confirm Accounts list loaded
    get_by_role("button", name="New")                            → New button
    get_by_role("dialog")                                        → record type modal scope
    dialog.get_by_text("Individual Account - Suspect")           → radio option (partial match)
    dialog.get_by_role("button", name="Next")                    → Next button (dialog-scoped)
    //h1[contains(.,name)]                                       → Account detail h1
    input[name="VRNA__First_Name__c"]                            → First Name field
    input[name="VRNA__Middle_Name__c"]                           → Middle Name field
    input[name="VRNA__Last_Name__c"]                             → Last Name field
"""

from pages.base.base_page import BasePage


class AccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Accounts nav tab — confirmed Codegen: get_by_role("link", name="Accounts")
        self.accounts_tab_role = "Accounts"

        # New button — confirmed Codegen: get_by_role("button", name="New")
        self.new_button_role = "New"

        # Name fields — confirmed from DOM: <input name="VRNA__First_Name__c" ...>
        self.first_name_input = 'input[name="VRNA__First_Name__c"]'
        self.middle_name_input = 'input[name="VRNA__Middle_Name__c"]'
        self.last_name_input = 'input[name="VRNA__Last_Name__c"]'


    # ── Navigation ──────────────────────────────────────────────────────────

    def go_to_accounts(self):
        """
        Navigate to the Accounts list page via the top nav tab.

        Falls back to a direct URL if the Accounts link is not found in the
        current app's navigation (e.g. when the session starts on the Logger
        Console app after Salesforce redirected there post-policy-creation).

        The direct URL navigation is retried once on transient network errors
        (ERR_NETWORK_CHANGED can occur when the previous page had pending
        requests that interfere with navigation).
        """
        try:
            self.page.get_by_role("link", name="Accounts").click()
            self.page.wait_for_url("**/o/Account/**", timeout=10000)
        except Exception:
            # Let any pending requests from the current page settle first
            try:
                self.page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                pass
            lightning_base = self.page.url.split('/lightning/')[0]
            target_url = f"{lightning_base}/lightning/o/Account/list"
            # Retry once for transient ERR_NETWORK_CHANGED errors
            for attempt in range(2):
                try:
                    self.page.goto(target_url)
                    self.page.wait_for_url("**/o/Account/**", timeout=15000)
                    break
                except Exception:
                    if attempt < 1:
                        self.page.wait_for_timeout(3000)
                    else:
                        raise
        self.page.wait_for_load_state("domcontentloaded")

    def click_new_button(self):
        """Click the New button on the Accounts list page."""
        self.page.get_by_role("button", name="New").click()

    # ── Record type selection ────────────────────────────────────────────────

    def select_individual_suspect_prospect(self):
        """
        Select the Individual Account - Suspect / Prospect radio button.

        Tries dialog-scoped click first (modal mode in My Agency app), then falls
        back to label click for full-page mode (Logger Console context).

        Full-page note: get_by_text().first may resolve to a hidden span in the
        Salesforce navigation layer before the visible label span. Clicking the
        wrapping <label> element is more reliable — it is always visible when
        the record type form is rendered.

        Confirmed selector (Codegen):
            dialog.get_by_text("Individual Account - Suspect")
        """
        text = "Individual Account - Suspect"
        try:
            dialog = self.page.get_by_role("dialog")
            dialog.get_by_text(text).first.click()
        except Exception:
            try:
                # Full-page mode: click the label wrapping the radio button
                self.page.locator("label").filter(has_text=text).first.click(timeout=5000)
            except Exception:
                # Last resort: force-click bypasses Playwright visibility check
                self.page.get_by_text(text).first.click(force=True)
        self.page.wait_for_timeout(800)

    def select_individual_customer(self):
        """
        Select the Individual Account - Customer radio button.

        Falls back to label click for full-page mode (Logger Console context).
        """
        text = "Individual Account - Customer"
        try:
            dialog = self.page.get_by_role("dialog")
            dialog.get_by_text(text).first.click()
        except Exception:
            try:
                self.page.locator("label").filter(has_text=text).first.click(timeout=5000)
            except Exception:
                self.page.get_by_text(text).first.click(force=True)
        self.page.wait_for_timeout(800)

    # ── Form fields ──────────────────────────────────────────────────────────

    def fill_name(self, first: str, last: str, middle: str = ""):
        """
        Fill the First, Middle, and Last Name fields on the account creation form.

        Scoped to the dialog and nth(0) — two identical input[name] fields exist
        in the same Contact Information section; we always target the first.
        Middle name is optional.
        """
        dialog = self.page.get_by_role("dialog")
        dialog.locator(self.first_name_input).nth(0).fill(first)
        if middle:
            dialog.locator(self.middle_name_input).nth(0).fill(middle)
        dialog.locator(self.last_name_input).nth(0).fill(last)

    # ── Verification ─────────────────────────────────────────────────────────

    def is_account_detail_visible(self, name: str) -> bool:
        """
        Returns True if the account detail page h1 contains the given name.
        Called after save() to confirm the account was created successfully.

        Args:
            name: First name or full name to look for in the page h1
        """
        self.page.wait_for_selector(f"//h1[contains(.,'{name}')]", timeout=30000)
        return self.page.is_visible(f"//h1[contains(.,'{name}')]")

