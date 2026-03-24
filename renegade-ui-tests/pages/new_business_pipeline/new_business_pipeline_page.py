"""
pages/new_business_pipeline/new_business_pipeline_page.py — Renegade UI Tests
================================================================================
Page Object for the New Business Pipeline tab and policy detail pages.

Covers:
    - Navigating to the pipeline list
    - Switching to the Pre-qualification list view
    - Opening a policy record from the list
    - Resetting the filter after each test (filter persists server-side)
    - Verifying the Send Intake Form button state (visible / active / disabled)
    - Handling the Send Intake Form confirmation modal
    - Verifying the intake form status card after reload

Confirmed selectors (Playwright Codegen):
    locator('[name="statusFilter"]')                    → Status filter dropdown
    locator(':text("MORE FILTERS")')                    → Expand more filters panel
    span[title*='Personal Auto']                        → LOB option span (CSS, pierces Shadow DOM)
    getByRole('button', name='Apply Filters').first     → Apply filter button (first of two)
    div.policy-account-info > a (nth 0)                 → First policy record link
    getByRole('button', name='Reset')                   → Reset filter button
"""

import re

from pages.base.base_page import BasePage


class NewBusinessPipelinePage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Top navigation — Pipelines tab
        self.pipeline_tab = 'a[title="Pipelines"]'

        # Sub-tabs inside Pipelines page — Prospects, Renewals, Cancellation
        self.prospects_subtab = '//a[contains(.,"Prospects")] | //li[contains(.,"Prospects")]//a'

        # Status filter — confirmed: locator('[name="statusFilter"]')
        self.status_filter_select = '[name="statusFilter"]'

        # More Filters toggle — confirmed: page.locator(':text("MORE FILTERS")')
        self.more_filters_toggle = ':text("MORE FILTERS")'

        # Send Intake Form button on the policy detail page
        # Salesforce renders action buttons as <a> or <button> inside force-record-layout
        self.send_intake_form_btn = '//a[contains(.,"Send Intake Form")] | //button[contains(.,"Send Intake Form")]'

        # Confirmation modal — confirm/send button inside the modal
        self.modal_confirm_button = '//div[contains(@class,"modal")]//button[contains(.,"Send") or contains(.,"Confirm") or contains(.,"Submit")]'
        self.modal_container = '.modal-container, [role="dialog"]'

        # Intake form status card — appears below status bar after form is sent + page reload
        self.intake_form_status_card = 'c-intake-form-status, [data-component-id*="intake"], .intake-form-card'

    # ── Navigation ──────────────────────────────────────────────────────────

    def go_to_pipeline(self):
        """
        Navigate to the Prospects pipeline.
        Steps:
            1. Click the Pipelines nav tab
            2. Click the Prospects sub-tab inside Pipelines
        """
        self.wait_for_element(self.pipeline_tab, timeout=30000)
        self.click(self.pipeline_tab)
        self.page.wait_for_load_state("load")
        self.wait_for_element(self.prospects_subtab, timeout=15000)
        self.click(self.prospects_subtab)
        self.page.wait_for_load_state("load")

    def filter_by_prequalification(self, lob: str = 'Personal Auto'):
        """
        Filter the Prospects pipeline list to Pre-Qualification + Line of Business.

        Steps:
            1. Select Pre-Qualification from the status filter
            2. Click MORE FILTERS to expand the additional filter panel
            3. Scroll to the Line of Business dropdown and select the given LOB
            4. Click Apply Filters — .first because two Apply buttons appear when
               More Filters is expanded (one in the main bar, one in the panel)

        Args:
            lob: Line of Business label to select (default: 'Personal Auto')

        Confirmed selectors:
            [name="statusFilter"]                               → Status dropdown
            :text("MORE FILTERS")                               → More filters toggle
            span[title*='Personal Auto']                        → LOB option span (CSS)
            getByRole('button', name='Apply Filters').first     → Apply button
        """
        # Step 0 — Reset any previously applied filters first.
        # A prior test run may have left filters applied (e.g. if teardown failed).
        # Resetting ensures lobFilter options are fully populated before selection.
        self._reset_if_present()

        # Step 1 — Status filter: Pre-Qualification
        self.page.locator(self.status_filter_select).wait_for(timeout=15000)
        self.page.locator(self.status_filter_select).select_option(label="Pre-Qualification")

        # Step 2 — Expand More Filters panel.
        # Confirmed selector via Codegen: div filtered by exact text "MORE FILTERS", nth(2)
        more_filters = self.page.locator("div").filter(has_text=re.compile(r"^MORE FILTERS$")).nth(2)
        more_filters.wait_for(timeout=10000)
        more_filters.click()
        self.page.wait_for_timeout(2000)  # Let the expanded panel and its options fully load

        # Step 3 — Select LOB from the native <select> element.
        # Confirmed via Playwright Codegen: the LOB filter is a native <select name="lobFilter">.
        # The select element only populates its options after MORE FILTERS is expanded.
        self.page.locator('select[name="lobFilter"]').select_option(lob)

        # Step 4 — Wait for LWC spinner then apply.
        # Use .first — two Apply Filters buttons exist when More Filters is open.
        try:
            self.page.locator('lightning-spinner').wait_for(state='hidden', timeout=10000)
        except Exception:
            pass  # Spinner may not always appear — continue if it never shows
        self.page.get_by_role('button', name='Apply Filters').first.click(force=True)
        self.page.wait_for_load_state("load")

    def open_first_record(self):
        """
        Click the first policy row link in the filtered pipeline list.

        Confirmed selector (Playwright Codegen):
            div.policy-account-info > a (nth 0) → first policy link in the list

        The LOB filter already restricts results to Personal Auto (or whichever
        LOB was selected in filter_by_prequalification), so no further type
        check is needed here — the first row is always the right type.
        """
        first_link = self.page.locator('div.policy-account-info').locator('a').nth(0)
        first_link.wait_for(timeout=20000)
        first_link.click()
        self.page.wait_for_load_state("networkidle", timeout=30000)

    def reset_filter(self):
        """
        Click the Reset button to clear the applied filter.

        The pipeline filter persists server-side across sessions.
        Call this after every test that applies a filter so the pipeline is
        not left in a filtered state for subsequent tests.

        Confirmed selector from DOM: button.reset-button
        """
        self.page.locator('button.reset-button').click()
        self.page.wait_for_load_state("domcontentloaded")

    def _reset_if_present(self):
        """
        Click Reset only if the button is currently visible.

        Called at the start of filter_by_prequalification() to clear any
        filters left by a previous test run before applying new ones.
        Silently skips if Reset is not present (no filters applied).
        """
        try:
            reset = self.page.locator('button.reset-button')
            reset.wait_for(state='visible', timeout=3000)
            reset.click()
            self.page.wait_for_timeout(1000)  # Let filter panel return to default state
        except Exception:
            pass  # No filters applied — safe to continue

    # ── Button state checks ──────────────────────────────────────────────────

    def is_send_intake_form_button_visible(self, timeout: int = 15000) -> bool:
        """
        Returns True if the Send Intake Form button is present on the page.

        Waits up to `timeout` ms for the button to appear — Salesforce Lightning
        components continue rendering after networkidle, so an instant is_visible()
        check races against LWC mount and returns False prematurely.
        """
        try:
            self.page.wait_for_selector(
                '//a[contains(.,"Send Intake Form")] | //button[contains(.,"Send Intake Form")]',
                timeout=timeout,
            )
            return True
        except Exception:
            return False

    def is_send_intake_form_button_active(self) -> bool:
        """
        Returns True if the Send Intake Form button is present AND enabled.
        A disabled button has aria-disabled="true" or the disabled attribute.
        """
        btn = (
            self.page.query_selector('//a[contains(.,"Send Intake Form")]')
            or self.page.query_selector('//button[contains(.,"Send Intake Form")]')
        )
        if not btn:
            return False
        disabled = btn.get_attribute("disabled") or btn.get_attribute("aria-disabled")
        return disabled is None or disabled == "false"

    def is_send_intake_form_button_disabled(self) -> bool:
        """
        Returns True if the Send Intake Form button is present but disabled.
        This is the expected state after the intake form is sent.
        """
        btn = (
            self.page.query_selector('//a[contains(.,"Send Intake Form")]')
            or self.page.query_selector('//button[contains(.,"Send Intake Form")]')
        )
        if not btn:
            return True  # Button gone entirely also means it can't be clicked
        disabled = btn.get_attribute("disabled") or btn.get_attribute("aria-disabled")
        return disabled is not None and disabled != "false"

    # ── Intake form actions ──────────────────────────────────────────────────

    def click_send_intake_form(self):
        """Click the Send Intake Form button to open the confirmation modal."""
        self.wait_for_element('//a[contains(.,"Send Intake Form")] | //button[contains(.,"Send Intake Form")]', timeout=15000)
        self.click('//button[contains(.,"Send Intake Form")]') if self.is_visible('//button[contains(.,"Send Intake Form")]') \
            else self.click('//a[contains(.,"Send Intake Form")]')

    def confirm_send_in_modal(self):
        """
        Wait for the confirmation modal to appear and click the confirm button.
        Handles the modal that appears after clicking Send Intake Form.
        """
        self.wait_for_element(self.modal_container, timeout=15000)
        self.wait_for_element(self.modal_confirm_button, timeout=10000)
        self.click(self.modal_confirm_button)
        # Wait for modal to close
        self.page.wait_for_selector(self.modal_container, state="hidden", timeout=15000)

    def reload_and_wait(self):
        """Reload the page and wait for Salesforce Lightning to fully render."""
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30000)

    # ── Post-send verification ───────────────────────────────────────────────

    def is_intake_form_status_card_visible(self) -> bool:
        """
        Returns True if the intake form status card is visible below the status bar.
        This card only appears after the intake form has been sent AND the page reloaded.
        """
        return (
            self.is_visible('c-intake-form-status')
            or self.is_visible('[data-component-id*="intake"]')
            or self.is_visible('.intake-form-card')
        )
