<!-- File: renegade-ui-tests/tests/ui/new_business_pipeline/test_intake_form.py -->

# Renegade : Intake Form — Pipeline Quick Check

## Purpose
Fast, non-destructive smoke test. No data creation.
Navigates directly to the New Business Pipeline and verifies the
Send Intake Form button is visible on a Pre-qualification record.

For the **full intake form flow** (account creation → policy creation →
send → modal → reload → status component), see:
`prompts/renegade-ui-tests/policy_intake_form.md`

## Before Each Test
- User is already logged in (`login` fixture)

---

## 1. Send Intake Form Button Visible (smoke — read-only)

### 1.1 Pre-qualification policy in the pipeline shows the Send Intake Form button
- Click the **Pipelines** tab in the navigation bar
- Click the **Prospects** sub-tab inside Pipelines
- Apply filter: Stage/Status = **Pre-Qualification**
- Open the first record from the filtered results
- The policy detail page loads
- The **Send Intake Form** button is visible on the page
- The button may be active OR disabled depending on whether the form was already sent
- This test only confirms the button is present — it does not check state or click it

---

> **Note:** This quick check uses existing pipeline data. For the complete
> end-to-end story with fresh data creation, see `policy_intake_form.md`.
