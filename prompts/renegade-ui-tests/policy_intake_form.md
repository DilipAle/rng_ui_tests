<!-- File: renegade-ui-tests/tests/ui/policy/test_policy_intake_form.py -->

# Renegade : Policy Page — Intake Form CTA

## Business Context
The Send Intake Form is a CTA action on the policy page.
It is only available on Pre-qualification policies for Personal Lines (Auto, Home)
and Commercial (Trucking) LOBs.

After the intake form is sent:
- The Send Intake Form action is disabled immediately
- Reloading the page reveals an Intake Form Status component below the status bar
- The action changes from "Send Intake Form" to "Resend"

## Setup for Each Test
- Create a new Individual Suspect/Prospect account with:
  - Unique first name, last name, phone, email (faker)
  - Physical address (faker street, city, TX, zip)
  - LOBs selected: Auto (Personal Lines), Home (Personal Lines), Trucking (Commercial)
- Salesforce auto-creates a Pre-qualification policy linked to the account
- Navigate to the policy via the related records section on the account page

## Teardown for Each Test
- Delete the account after the test
- The linked policy is removed with it

---

## 1. Send Intake Form CTA Visible (smoke)

### 1.1 Policy page shows Send Intake Form as an active CTA action
- Navigate to the policy page (via account creation flow)
- The policy is in Pre-qualification status
- The **Send Intake Form** CTA action is visible on the page
- The button is **active/enabled** — the user can click it
- No intake form status component is visible yet (form not yet sent)

---

## 2. Full Intake Form Flow (e2e)

### 2.1 Sending intake form disables the CTA and shows status component + Resend after reload

**Step 1 — Verify CTA is active:**
- Navigate to the policy page
- Send Intake Form CTA is visible and enabled

**Step 2 — Send the intake form:**
- Click Send Intake Form
- A confirmation modal appears
- Click the confirm/send button in the modal
- Modal closes
- Send Intake Form CTA is now **disabled** (cannot be clicked again)

**Step 3 — Reload and verify component + Resend:**
- Reload the page
- Wait for the page to fully load
- The **Intake Form Status component** is visible below the status bar
- The **Resend** action button is visible
- Send Intake Form CTA is no longer active

**Step 4 — Resend flow (verify modal appears):**
- Click the Resend button
- A confirmation modal appears (same flow as Send)
- Click confirm in the modal
- Modal closes
- Resend button remains **available** — user can resend multiple times

---

## Data Rules
- First name: `fake.first_name()`
- Last name: `fake.last_name()`
- Phone: `"2" + fake.numerify("#########")` — 10-digit US
- Email: `fake.unique.email()`
- Street: `fake.street_address()`
- City: `fake.city()`
- State: `"TX"`
- Zip: `fake.numerify("#####")`
- LOBs: Auto, Home (Personal Lines) + Trucking (Commercial)
