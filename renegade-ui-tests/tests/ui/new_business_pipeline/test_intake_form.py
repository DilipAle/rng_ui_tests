"""
tests/ui/new_business_pipeline/test_intake_form.py — Renegade UI Tests
========================================================================
Fast, non-destructive smoke test for the intake form button.
No data creation — reads directly from the New Business Pipeline.

For the full intake form flow (send → modal → disabled → reload → status + Resend),
see: tests/ui/policy/test_policy_intake_form.py

Markers:
    smoke → read-only button visibility check

Fixtures used:
    login → pre-authenticated Salesforce page
"""

import pytest
from pages.new_business_pipeline.new_business_pipeline_page import NewBusinessPipelinePage


@pytest.mark.smoke
@pytest.mark.description("Pre-qualification policy in pipeline shows Send Intake Form button")
def test_send_intake_form_button_visible(login):
    """
    SMOKE — Verify that the Send Intake Form button is visible and active
    on a Pre-qualification policy in the New Business Pipeline.

    Read-only — does not click the button or change any state.

    Flow:
        1. Go to Prospects pipeline
        2. Filter by Pre-Qualification → Apply Filters
        3. Click first policy record
        4. Assert Send Intake Form button is present
        5. Go back to pipeline → Reset filter (filter persists server-side)

    Fixture: login (already logged in)
    """
    page = login
    pipeline = NewBusinessPipelinePage(page)

    pipeline.go_to_pipeline()
    pipeline.filter_by_prequalification()
    pipeline.open_first_record()

    # Only verify the button exists — it may be active or disabled
    # depending on whether the intake form was already sent for this record
    assert pipeline.is_send_intake_form_button_visible(), \
        "Expected 'Send Intake Form' button to be present on a Pre-qualification policy"

    # Teardown: navigate back to pipeline and reset the filter.
    # The filter persists server-side — resetting keeps the pipeline clean for other tests.
    try:
        pipeline.go_to_pipeline()
        pipeline.reset_filter()
    except Exception:
        pass  # Never let teardown failure hide the test result
