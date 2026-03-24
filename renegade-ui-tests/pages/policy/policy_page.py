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
        → select Agency (required field)
        → select Branch (required field)
        → click Save
        → verify toast message

Confirmed selectors:
    getByRole('button', name='New PL Policy')        → New PL Policy button
    locator('a').filter(has_text='--None--').first → Coverage type dropdown
    getByRole('option', name=coverage_type)          → Coverage type option
    getByRole('textbox', name='Effective Date')      → Effective date field
    getByRole('textbox', name='Expiration Date')     → Expiration date field
    Agency field: get_by_role('combobox', name='Agency') OR XPath label-scoped
    getByRole('dialog').getByRole('button', name='Save') → Save button
"""

import re
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

        Stores the account detail URL so save_policy() can navigate back to
        the Policies related list if Salesforce redirects elsewhere after save.
        """
        # Capture account URL — needed if post-save redirect goes to Log__c
        self._account_url = self.page.url
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
        self.page.locator('a').filter(has_text='--None--').first.click()
        # Lightning combobox options render with role="option", not role="button"
        self.page.get_by_role('option', name=coverage_type).click()

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

    def select_agency(self, agency: str = None):
        """
        Select an agency from the required Agency dropdown in the New PL Policy form.

        The Agency field is a required picklist. Scopes all selectors to the
        .slds-form-element whose text starts with 'Agency' — anchored via regex
        to exclude 'Target Agency Commission $' (also contains 'Agency').

        If no agency name is given, the first available non-None option is selected
        automatically — resilient to org-specific agency names.

        Args:
            agency: Exact agency name to select. If None, auto-selects first option.

        Trigger strategy (tried in order):
            1. Native <select>          — simplest; select_option() handles it directly
            2. <input> inside combobox  — LWC lightning-combobox trigger (most common)
            3. Any readonly <input>     — alternative LWC rendering
            4. <a> with '--None--'      — link-style combobox (like Coverage Type field)
            5. Any <a> in container     — broadest anchor fallback
        Note: <button>.first is intentionally avoided — the first <button> in the
        Agency .slds-form-element is the ℹ️ info icon in the label, not the dropdown.
        """
        dialog = self.page.get_by_role('dialog')

        # CSS filter() pierces Salesforce LWC shadow DOM automatically.
        # re.compile(r'^Agency') anchors to text-start, excluding 'Target Agency…'.
        agency_container = (
            dialog.locator('.slds-form-element')
            .filter(has_text=re.compile(r'^Agency'))
            .first
        )
        agency_container.wait_for(timeout=10000)

        # ── Try native <select> first (simplest — no option-click needed) ──────
        try:
            sel = agency_container.locator('select').first
            sel.wait_for(timeout=1500)
            if agency:
                sel.select_option(label=agency)
            else:
                sel.select_option(index=1)  # 0 = --None--, 1 = first real value
            return
        except Exception:
            pass

        # ── Open the dropdown ─────────────────────────────────────────────────
        # Try each trigger selector in order; stop at the first that works.
        # <button> is deliberately excluded: agency_container.locator('button').first
        # resolves to the ℹ️ info icon in the label, not the dropdown toggle.
        triggered = False
        trigger_selectors = [
            '[role="combobox"] input',   # <input> nested inside the combobox div
            'input[readonly]',           # readonly input (LWC lightning-combobox)
            'input',                     # any input (broadest input fallback)
            'a',                         # link-style dropdown (Coverage-Type pattern)
        ]
        for selector in trigger_selectors:
            if triggered:
                break
            try:
                el = agency_container.locator(selector).first
                el.wait_for(timeout=1000)
                el.click()
                triggered = True
            except Exception:
                pass

        if not triggered:
            raise Exception(
                'select_agency: could not interact with Agency dropdown — '
                'inspect the form DOM to identify the correct selector'
            )

        self.page.wait_for_timeout(300)

        if agency:
            self.page.get_by_role('option', name=agency).click()
        else:
            # get_by_role uses the accessibility tree — handles shadow DOM and
            # visibility natively. Selects the first visible non-None option.
            self.page.get_by_role('option').filter(has_not_text='--None--').first.click(timeout=5000)

    def select_branch(self, branch: str = None):
        """
        Select a branch from the required Branch dropdown in the New PL Policy form.

        Branch is a required picklist that appears below Agency. Its available
        options depend on the selected Agency value.

        If no branch name is given, the first available non-None option is selected
        automatically.

        Args:
            branch: Exact branch name to select. If None, auto-selects first option.
        """
        dialog = self.page.get_by_role('dialog')

        # Branch starts with "Branch" — no ambiguity with other field names.
        branch_container = (
            dialog.locator('.slds-form-element')
            .filter(has_text=re.compile(r'^Branch'))
            .first
        )
        branch_container.wait_for(timeout=10000)

        # ── Try native <select> first ──────────────────────────────────────────
        try:
            sel = branch_container.locator('select').first
            sel.wait_for(timeout=1500)
            if branch:
                sel.select_option(label=branch)
            else:
                sel.select_option(index=1)
            return
        except Exception:
            pass

        # ── Open the dropdown ─────────────────────────────────────────────────
        triggered = False
        trigger_selectors = [
            '[role="combobox"] input',
            'input[readonly]',
            'input',
            'a',
        ]
        for selector in trigger_selectors:
            if triggered:
                break
            try:
                el = branch_container.locator(selector).first
                el.wait_for(timeout=1000)
                el.click()
                triggered = True
            except Exception:
                pass

        if not triggered:
            raise Exception(
                'select_branch: could not interact with Branch dropdown — '
                'inspect the form DOM to identify the correct selector'
            )

        self.page.wait_for_timeout(300)

        if branch:
            self.page.get_by_role('option', name=branch).click()
        else:
            self.page.get_by_role('option').filter(has_not_text='--None--').first.click(timeout=5000)

    def _navigate_to_latest_policy(self, coverage_type='Personal Auto'):
        """
        Navigate to the most recently created policy on the account's Policies tab.

        Called after save_policy() completes. The Quick Action save lands on the
        account detail page (or briefly on Log__c before redirecting back). This
        method navigates to the account, opens the Policies tab, waits for the
        related list to render, then navigates directly to the policy record.

        Navigation strategy — policy link:
            The related-list link text is the coverage type (e.g. 'Personal Auto').
            Playwright's get_by_role('link') uses the accessibility tree which
            pierces BOTH open and closed shadow DOM — more reliable than CSS
            selectors for Salesforce's <lightning-formatted-url> components.
            After the link is found, page.goto(href) is used for direct navigation
            so that Logger Console workspace-subtab behavior doesn't interfere.

        Args:
            coverage_type: Coverage type label used to identify the policy row
                           (e.g. 'Personal Auto'). Defaults to 'Personal Auto'.

        Requires click_new_pl_policy() to have been called first (stores _account_url).
        """
        account_url = getattr(self, '_account_url', None)
        if not account_url:
            return

        # Return to the account detail page and wait for Lightning to render
        self.page.goto(account_url)
        self.page.wait_for_load_state('domcontentloaded', timeout=30000)
        self.page.wait_for_timeout(2000)  # Allow Lightning components to initialise

        # Click the Policies tab — try multiple label variants used across orgs
        for tab_name in ['Policies', 'PL Policies', 'Policy']:
            try:
                self.page.get_by_role('tab', name=tab_name).click(timeout=5000)
                self.page.wait_for_load_state('domcontentloaded', timeout=15000)
                self.page.wait_for_timeout(3000)  # Let related-list rows render
                break
            except Exception:
                pass

        # ── Find the policy link href and navigate directly ────────────────────
        # get_by_role uses the accessibility tree — pierces ALL shadow DOM.
        # We extract the href and call goto() rather than click() to guarantee
        # a full address-bar navigation even in Lightning Console apps (where
        # click() opens a workspace subtab without changing the URL).
        policy_href = None

        # Strategy 1: find by coverage type label (most precise)
        try:
            link = self.page.locator('table').get_by_role('link', name=coverage_type).first
            link.wait_for(timeout=10000)
            policy_href = link.get_attribute('href')
        except Exception:
            pass

        # Strategy 2: find any link in the table if coverage-type match fails
        if not policy_href:
            try:
                link = self.page.locator('table tbody').get_by_role('link').first
                link.wait_for(timeout=5000)
                policy_href = link.get_attribute('href')
            except Exception:
                pass

        # Strategy 3: JS shadow-DOM traversal — searches by coverage type text
        if not policy_href:
            try:
                policy_href = self.page.evaluate("""
                    (coverageType) => {
                        function findLinks(root) {
                            const results = [];
                            try {
                                root.querySelectorAll('a[href]').forEach(a => {
                                    const text = a.textContent.trim();
                                    if (text === coverageType && a.href.includes('/r/')) {
                                        results.push(a.href);
                                    }
                                });
                                root.querySelectorAll('*').forEach(el => {
                                    if (el.shadowRoot) results.push(...findLinks(el.shadowRoot));
                                });
                            } catch (e) {}
                            return results;
                        }
                        return findLinks(document)[0] || null;
                    }
                """, coverage_type)
            except Exception:
                pass

        if policy_href:
            # Ensure it's an absolute Lightning URL before navigating.
            #
            # Salesforce related-list links can return CLASSIC record URLs
            # (e.g. '/a0WOy00000B5okDMAR' — just the record ID). Navigating
            # to a classic URL with goto() bypasses Lightning's JS router and
            # Salesforce serves the page via /_classic/..., which renders the
            # old Visualforce UI without Lightning Web Components (no Send Intake
            # Form button).
            #
            # Convert classic URLs to Lightning format: /lightning/r/{id}/view
            # Salesforce Lightning supports record-ID-only navigation and resolves
            # the object type automatically.
            base = self.page.url.split('/lightning/')[0]
            if not policy_href.startswith('http'):
                if policy_href.startswith('/lightning/'):
                    policy_href = base + policy_href
                else:
                    # Classic URL: strip leading slash, treat remainder as record ID
                    record_id = policy_href.lstrip('/')
                    policy_href = f'{base}/lightning/r/{record_id}/view'
            self.page.goto(policy_href)
            self.page.wait_for_load_state('domcontentloaded', timeout=30000)
            # networkidle waits for Lightning LWC components to finish loading.
            # Navigating from Logger Console to My Agency triggers an app switch
            # that takes significantly longer than domcontentloaded.
            try:
                self.page.wait_for_load_state('networkidle', timeout=30000)
            except Exception:
                # networkidle may not settle cleanly in Lightning SPA; fall back
                self.page.wait_for_timeout(5000)
            self.page.wait_for_timeout(2000)  # Extra buffer for LWC rendering

    def save_policy(self, coverage_type='Personal Auto'):
        """
        Click Save to create the policy, then navigate to the policy detail page.

        Scoped to the dialog — clicks the button directly, not the inner span
        (span has pointer-events:none and is not clickable).

        Polls up to 10 s for Save to become enabled, then clicks.

        Save completion strategy:
            The 'New PL Policy' Quick Action opens as a MODAL on the account detail
            page — the URL does NOT change when the form opens or saves. A
            wait_for_url() check immediately returns True (current URL never had
            'action/quick') before the save completes. Instead, wait for the dialog
            to close (indicating the AJAX save finished), then navigate explicitly to
            the policy via _navigate_to_latest_policy().

        Args:
            coverage_type: Coverage type created — passed to _navigate_to_latest_policy
                           so it can find the correct policy link by label text.
        """
        save_btn = self.page.get_by_role('dialog').get_by_role('button', name='Save')
        # Poll until not disabled (max 10 s in 300 ms steps)
        for _ in range(34):
            try:
                disabled = save_btn.get_attribute('disabled')
                aria_disabled = save_btn.get_attribute('aria-disabled')
                if disabled is None and aria_disabled != 'true':
                    break
            except Exception:
                pass
            self.page.wait_for_timeout(300)
        save_btn.click()

        # Wait for the Quick Action dialog to close — this signals save completion.
        # If the Quick Action opened as a full-page flow instead (URL changed), the
        # dialog wait will timeout quickly and the except block is a no-op.
        try:
            self.page.get_by_role('dialog').wait_for(state='hidden', timeout=30000)
        except Exception:
            pass

        # Allow any post-save redirect chain (e.g. Log__c → back to account) to settle
        try:
            self.page.wait_for_load_state('domcontentloaded', timeout=15000)
        except Exception:
            pass
        self.page.wait_for_timeout(2000)

        # Always navigate to the most recently created policy record.
        # The dialog-close wait above ensures the save has completed before we navigate.
        self._navigate_to_latest_policy(coverage_type=coverage_type)

    # ── Full policy creation in one call ─────────────────────────────────────

    def create_pl_policy(
        self,
        coverage_type: str = 'Personal Auto',
        effective_date: str = None,
        expiration_date: str = None,
        agency: str = None,
        branch: str = None,
    ):
        """
        Complete the full New PL Policy creation flow from the account detail page.

        Args:
            coverage_type:   Coverage type (default: 'Personal Auto')
            effective_date:  MM/DD/YYYY — defaults to today
            expiration_date: MM/DD/YYYY — defaults to 1 year from today
            agency:          Agency name to select — if None, auto-selects first option
            branch:          Branch name to select — if None, auto-selects first option

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
        self.select_agency(agency)
        self.select_branch(branch)
        self.save_policy(coverage_type=coverage_type)

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
