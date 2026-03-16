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
"""

from pages.base.base_page import BasePage


class AccountPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Accounts nav tab — confirmed Codegen: get_by_role("link", name="Accounts")
        self.accounts_tab_role = "Accounts"

        # New button — confirmed Codegen: get_by_role("button", name="New")
        self.new_button_role = "New"


    # ── Navigation ──────────────────────────────────────────────────────────

    def go_to_accounts(self):
        """
        Navigate to the Accounts list page via the top nav tab.

        Uses wait_for_url to confirm the Accounts list is loaded before
        proceeding — prevents accidentally clicking a New button from
        whatever page was previously open.
        """
        self.page.get_by_role("link", name="Accounts").click()
        self.page.wait_for_url("**/o/Account/**", timeout=15000)
        self.page.wait_for_load_state("domcontentloaded")

    def click_new_button(self):
        """Click the New button on the Accounts list page."""
        self.page.get_by_role("button", name="New").click()

    # ── Record type selection ────────────────────────────────────────────────

    def select_individual_suspect_prospect(self):
        """
        Select the Individual Account - Suspect / Prospect radio button.

        Scoped to the dialog to avoid matching account rows in the background list.
        wait_for_timeout(800) lets LWC re-render after selection before Next is clicked.

        Confirmed selector (Codegen):
            dialog.get_by_text("Individual Account - Suspect")
        """
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_text("Individual Account - Suspect").click()
        self.page.wait_for_timeout(800)  # LWC re-renders the dialog after selection

    def select_individual_customer(self):
        """
        Select the Individual Account - Customer radio button.

        Scoped to the dialog to avoid matching account rows in the background list.

        Confirmed selector (Codegen):
            dialog.get_by_text("Individual Account - Customer")
        """
        dialog = self.page.get_by_role("dialog")
        dialog.get_by_text("Individual Account - Customer").click()
        self.page.wait_for_timeout(800)  # LWC re-renders the dialog after selection

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

