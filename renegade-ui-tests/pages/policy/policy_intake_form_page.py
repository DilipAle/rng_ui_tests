"""
pages/policy/policy_intake_form_page.py — Renegade UI Tests
=============================================================
Page Object for the Intake Form CTA on the Salesforce policy detail page.

All selectors below are confirmed against the live QA app via Playwright Codegen.

Covers:
    - Checking Send Intake Form CTA visibility and active/disabled state
    - Clicking Send Intake Form and confirming the outreach modal
    - Verifying the toast message after sending
    - Checking the send-intake-frame component visibility after send
    - Checking the Send Reminder button visibility and clicking it
    - Confirming the Send Reminder modal

Used by:
    tests/ui/policy/test_policy_intake_form.py

Confirmed selectors (from Codegen on live QA):
    button:has-text("Send Intake Form")          → Send Intake Form CTA
    div.send-outreach-body                        → Confirmation modal container
    button.send-outreach-btn-primary              → Confirm/Send button inside modal
    text=Outreach created successfully.           → Toast message after send
    div.send-intake-frame                         → Intake details frame after send
    button:has-text("Send Reminder")              → Send Reminder CTA (replaces Resend)
"""

from pages.base.base_page import BasePage


class PolicyIntakeFormPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Send Intake Form CTA — confirmed via Codegen
        self.send_intake_form_cta = 'button:has-text("Send Intake Form")'

        # Send Reminder CTA — appears after intake form is sent and page reloaded
        # Note: the UI shows "Send Reminder", not "Resend"
        self.send_reminder_cta = 'button:has-text("Send Reminder")'

        # Confirmation modal container — confirmed via Codegen
        self.modal_container = 'div.send-outreach-body'

        # Confirm/Send button inside the modal — confirmed via Codegen
        self.modal_confirm_button = 'button.send-outreach-btn.send-outreach-btn-primary'

        # Toast message that appears after successful send — confirmed via Codegen
        self.toast_message = 'text=Outreach created successfully.'

        # Intake form details frame — appears below status bar after send
        # confirmed via Codegen
        self.intake_form_frame = 'div.send-intake-frame'

    # ── CTA visibility ───────────────────────────────────────────────────────

    def is_send_intake_form_visible(self) -> bool:
        """
        Returns True if the Send Intake Form CTA is present on the page.

        Uses get_by_role() (accessibility tree) rather than a CSS selector so
        that closed Salesforce LWC shadow DOM is pierced reliably. Also waits
        up to 15 s for the LWC component to render — page.is_visible() returns
        immediately and fails if called before Lightning finishes rendering.
        """
        try:
            btn = self.page.get_by_role('button', name='Send Intake Form')
            btn.wait_for(timeout=15000)
            return btn.is_visible()
        except Exception:
            return False

    def is_send_intake_form_active(self) -> bool:
        """
        Returns True if the Send Intake Form CTA is present and enabled.
        Checks aria-disabled and disabled attributes.
        Uses get_by_role() to pierce closed LWC shadow DOM.
        """
        try:
            btn = self.page.get_by_role('button', name='Send Intake Form')
            btn.wait_for(timeout=15000)
            disabled = btn.get_attribute("disabled")
            aria_disabled = btn.get_attribute("aria-disabled")
            return disabled is None and aria_disabled != 'true'
        except Exception:
            return False

    def is_send_intake_form_disabled(self) -> bool:
        """Returns True if the Send Intake Form CTA is disabled or gone."""
        try:
            btn = self.page.get_by_role('button', name='Send Intake Form')
            btn.wait_for(timeout=5000)
            disabled = btn.get_attribute("disabled")
            aria_disabled = btn.get_attribute("aria-disabled")
            return disabled is not None or aria_disabled == 'true'
        except Exception:
            return True  # Gone entirely — cannot be clicked

    def is_send_reminder_visible(self) -> bool:
        """Returns True if the Send Reminder CTA is visible on the page."""
        return self.is_visible(self.send_reminder_cta)

    # kept as alias so existing test calls to is_resend_visible() still work
    def is_resend_visible(self) -> bool:
        """Alias for is_send_reminder_visible() — kept for backwards compatibility."""
        return self.is_send_reminder_visible()

    def is_intake_form_status_component_visible(self) -> bool:
        """
        Returns True if the intake form details frame is visible.
        This frame appears below the status bar after the intake form is sent.
        Confirmed selector: div.send-intake-frame
        """
        return self.is_visible(self.intake_form_frame)

    def is_toast_visible(self) -> bool:
        """Returns True if the success toast 'Outreach created successfully.' is visible."""
        return self.is_visible(self.toast_message)

    # ── CTA actions ──────────────────────────────────────────────────────────

    def click_send_intake_form(self):
        """Click the Send Intake Form CTA to open the confirmation modal."""
        self.wait_for_element(self.send_intake_form_cta, timeout=15000)
        self.click(self.send_intake_form_cta)

    def click_resend(self):
        """Click the Send Reminder CTA to open the confirmation modal."""
        self.wait_for_element(self.send_reminder_cta, timeout=15000)
        self.click(self.send_reminder_cta)

    def confirm_modal(self):
        """
        Wait for the outreach confirmation modal and click the primary send button.
        Used for both Send Intake Form and Send Reminder flows.

        Modal container:  div.send-outreach-body
        Confirm button:   button.send-outreach-btn.send-outreach-btn-primary
        """
        self.wait_for_element(self.modal_container, timeout=15000)
        self.wait_for_element(self.modal_confirm_button, timeout=10000)
        self.click(self.modal_confirm_button)
        self.page.wait_for_selector(self.modal_container, state="hidden", timeout=15000)

    def wait_for_toast(self):
        """Wait for the success toast to appear after sending."""
        self.wait_for_element(self.toast_message, timeout=15000)

    def reload_and_wait(self):
        """Reload the page and wait for Salesforce Lightning to fully render."""
        self.page.reload()
        self.page.wait_for_load_state("networkidle", timeout=30000)
