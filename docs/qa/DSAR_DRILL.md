# DSAR Drill — end-to-end simulation

Run this once before go-live and again every 6 months. Validates that
we can satisfy a data subject's access request within the shortest
applicable window (45 days for California, 30 days elsewhere).

---

## Setup (5 min)

1. Scratch workspace logged in as a Compliance Officer or DPO.
2. Seed a realistic "subject" whose data lives in multiple registers:
   - Add a processing activity named `Customer onboarding` with
     `data_subject_categories=['customers']`
   - Generate one template document addressed to the subject
   - Log 2 support-ticket-like notes in a fake CRM (out of band)

---

## Scenario injection (1 min)

> **Oma Adeyemi (`oma@example.com`, Nigeria) emails us at 09:12 asking
> for "everything you hold on me" under the NDPA.**

---

## Phase 1 — Intake (target: ≤ 1 business day)

| # | Action | ✓ |
|---|---|---|
| 1.1 | Log a DSAR in `/dsar/new/` — type `access`, country `NG`, copy the email verbatim into notes | |
| 1.2 | Confirm the system set a 30-day due-at | |
| 1.3 | Send the subject an acknowledgement (simulated — save to notes) confirming receipt + that the clock has started | |
| 1.4 | Verify identity (strip from a known-good email? ID copy? MFA challenge?) — record the method in notes | |
| 1.5 | Assign the DSAR to a named owner | |

**Acceptance:** intake recorded within 1 business day; identity check
documented; status moved to `Verifying identity`.

---

## Phase 2 — Discovery (target: ≤ 10 business days)

Use the platform itself as the map of where data lives. For each register,
query for the subject's identifier and record results in the DSAR note:

| Register | Query | Result |
|---|---|---|
| ProcessingActivity | Does any activity involve this customer category + this subject? | ... |
| Control / Evidence | Any evidence mentioning the subject's name/email? | ... |
| Risk notes | Any free-text reference? | ... |
| Incident records | Was the subject in any breach register? | ... |
| AuthEvent (if they're also an app user) | Login history | ... |
| External systems | CRM, ticketing, BI, data warehouse | ... |

Move DSAR status to `In progress`.

---

## Phase 3 — Assembly (target: ≤ 15 business days)

1. Collect data into a structured package. For app-user data, use the
   platform's own export: `POST /accounts/me/export/` run by the subject,
   OR use admin to assemble on their behalf.
2. Redact third-party personal data that would otherwise leak.
3. Generate the DSAR **response letter** from the template library
   (`/templates/` → DSAR Response). Fill in data categories, sources,
   recipients, retention, rights.
4. Produce the bundle — JSON export + PDF letter + attachments —
   encrypted with a password the subject can verify (shared out-of-band).

---

## Phase 4 — Delivery (target: ≤ 30 days from intake)

1. Send the bundle to the subject.
2. Mark the DSAR `Closed` + record `closed_at`.
3. Record:
   - Response-time in days
   - Bytes delivered
   - Any data refusal + justification (Art. 15(4) third-party rights,
     legal hold, etc.)

**Acceptance:** the DSAR is closed at or before the 30-day mark
(45 days if the subject is in California).

---

## Metrics to capture every quarter

| Metric | Target | Q1 | Q2 | Q3 | Q4 |
|---|---|---|---|---|---|
| Median response time (days) | ≤ 20 |  |  |  |  |
| p95 response time (days) | ≤ 30 |  |  |  |  |
| % on-time (within jurisdiction window) | 100% |  |  |  |  |
| Refusals documented | ≤ 5% |  |  |  |  |
| Identity-verification failures | n/a track |  |  |  |  |

Feed these back into a Celery-scheduled report.

---

## Sign-off

| Role | Name | Date | Passed within SLA? |
|---|---|---|---|
| DPO |  |  |  |
| Compliance Officer |  |  |  |
