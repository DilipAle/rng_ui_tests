<!-- File: renegade-ui-tests/tests/ui/policy/test_policy_intake_form.py -->

# Renegade : Policy Page — Intake Form Full Flow

## Business Context
The Send Intake Form is a CTA action on the policy detail page.
It is only available on Pre-qualification policies for Personal Lines (Auto, Home)
and Commercial (Trucking) LOBs.

After the intake form is sent:
- The Send Intake Form action is disabled immediately
- Reloading the page reveals an Intake Form Status component below the status bar
- The action changes to "Send Reminder"

---

## Complete Flow (create account → create policy → intake form → reload → component)

### Setup for Each Test
- Create a new Individual Suspect/Prospect account with unique faker data:
  - First name, last name, phone, email
- On the account detail page, click **New PL Policy**
- Fill the New PL Policy form:
  - Policy / Coverage Type: **Personal Auto**
  - Effective Date: today
  - Expiration Date: 1 year from today
  - Agency: first available option in the dropdown
- Save → Salesforce navigates to the policy detail page

### Teardown for Each Test
- Navigate back to the account and delete it
- The linked policy is removed with the account

---

## 1. Send Intake Form CTA Visible (smoke — read-only)

### 1.1 Policy page shows Send Intake Form as an active CTA
- Create account → create Personal Auto policy via **New PL Policy**
- Navigate to the policy detail page (Pre-qualification status)
- The **Send Intake Form** CTA is **visible and active/enabled**
- No Intake Form Status component is visible yet (form not yet sent)
- **Do NOT click the CTA** — this test is read-only

---

## 2. Full Intake Form Flow (e2e — single combined flow)

This is the primary E2E test. It proves the complete story end-to-end:
account creation → policy creation → intake form send → modal → reload → status component.

### Step 1 — Account and Policy Setup
- Create a new Individual Suspect/Prospect account (faker: first name, last name, phone, email)
- Click **New PL Policy** on the account detail page
- Fill form: Coverage Type = Personal Auto, dates = today / +1yr, Agency = first available
- Save → policy detail page opens

### Step 2 — Verify Send Intake Form CTA is active
- The **Send Intake Form** CTA is visible on the policy detail page
- The CTA is **enabled** — the user can click it
- No Intake Form Status component is visible yet

### Step 3 — Click Send Intake Form → modal appears
- Click the **Send Intake Form** CTA
- A **confirmation popup/modal** appears

### Step 4 — Confirm → CTA disabled
- Click the confirm button in the modal
- The modal closes
- A success toast appears: *"Outreach created successfully."*

### Step 5 — Reload → Intake Form Status component visible
- Reload the page and wait for it to fully load
- The **Intake Form Status component** is visible below the status bar
- The **Send Reminder** CTA is visible

---

## Data Rules
- First name: `fake.unique.first_name()`
- Last name: `fake.unique.last_name()`
- Phone: `fake.unique.numerify("2#########")` — 10-digit US
- Email: `fake.unique.email()`
