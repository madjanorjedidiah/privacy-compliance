# Incident Drill — 90-minute tabletop

Exercises the **detection → containment → notification → closure** loop
that GDPR Art. 33 and Ghana DPA s.43 / NDPA s.40 require. Run once per
quarter, within 90 days of go-live, and whenever the team composition
materially changes.

Target duration: 90 minutes. Minimum participants: DPO, an engineer,
and a member of customer-comms / support.

---

## Pre-brief (5 min)

1. Re-state the scope: this is a **tabletop** — no production systems
   are touched. Everything is logged in a scratch workspace.
2. Appoint a scribe. They own the shared doc + the timer.
3. Open the platform in a staging tenant named **"drill-Q?-YYYY"** with
   the Owner account logged in.

## Scenario injection (5 min)

> **The SIEM alerts you at 09:14 that a small text file has been
> uploaded to a public-facing S3 bucket your product uses for receipts.
> The file contains 412 email addresses and hashed customer IDs. No
> passwords or card data. You have no evidence yet that the file was
> accessed externally.**

The scribe writes this into the incident log.

---

## T+0 — Detection (10 min)

The engineer logs an incident in `/incidents/new/`:

- Title: "Receipts bucket object briefly public"
- Severity: High (data exposed)
- Status: `Triaged`
- Detected at: current UTC
- Affected subjects estimate: 412
- Affected jurisdictions: `['EU','GH','KE']` (example; match drill reality)

**Acceptance:** the regulator deadline on the incident record is
≤ 72 hours from detection, and has been reduced if any jurisdiction in
the list has a shorter window. Screenshot for the log.

---

## T+15 — Containment (15 min)

Work through this script:

| # | Action | Who | ✓ |
|---|---|---|---|
| 1 | Bucket policy flipped back to private | Engineer | |
| 2 | CloudFront / CDN cache invalidated | Engineer | |
| 3 | Access-log sample pulled (what IPs, how many GETs) | Engineer | |
| 4 | Impacted customers enumerated from the file | DPO | |
| 5 | Runbook entry added to the incident's notes | Scribe | |

**Acceptance:** the bucket is private again; we have a count of
external accesses (even if zero).

---

## T+30 — Risk + harm assessment (10 min)

DPO fills the incident notes with:

- **Nature** — confidentiality breach, minor.
- **Categories** — contact details + hashed IDs. No financial, no health,
  no children's data.
- **Likely harm** — low: phishing lure at most; no direct financial risk.
- **Communication decision** — notify supervisory authorities that are
  applicable; hold individual notification unless high-risk threshold
  crossed (GDPR Art. 34).

---

## T+40 — Regulator notification (15 min)

Open the platform's **"Regulator Breach Notification Letter"** template
(`/templates/`) and generate it for the affected jurisdictions.

**Acceptance:** the generated letter includes the organisation name, a
concrete description, category counts, current containment, mitigation
plan, and the DPO's contact block. Save the PDF/markdown in the
incident's `notes`.

Send-simulation steps (do **not** email regulators in a drill):

- [ ] Letter addressed to the Ghana Data Protection Commission
- [ ] Letter addressed to the lead EU supervisory authority
- [ ] Letter addressed to the Kenya ODPC
- [ ] Submitted-at timestamp entered into the incident's "regulator
      notified at" field

Click **"Mark regulator notified"** on the incident detail page —
verify the green status pill appears and `regulator_notified_at` is set.

---

## T+55 — Customer comms (10 min)

Decide whether to notify data subjects directly (Art. 34). In this
drill: **no** — hashed IDs + emails only. Document the reasoning in the
incident notes.

Draft a **proactive FAQ / status page post** so support can respond
consistently to inbound questions. Attach to incident notes.

---

## T+65 — Closure (10 min)

On the incident detail page:

- [ ] Status set to `Resolved`
- [ ] `resolved_at` stamped
- [ ] Post-mortem action items logged (see next step)

Create 3-5 follow-up actions in the risk register:

1. Permanent S3 bucket public-access-block enforcement — owner, due date
2. Daily linting job for bucket ACLs — owner, due date
3. Breach-playbook update — owner, due date

---

## T+75 — Lessons learned (10 min)

Scribe reads the log back. Participants answer:

- What would have made detection 10 minutes faster?
- What would have slowed us down if the data was more sensitive?
- Any gaps in the template or the platform UX?
- Should any of these responses become periodic tasks in Celery Beat?

Export the incident record (view → browser print to PDF) and file under
`docs/incidents/drills/{YYYY-QN}/`.

---

## Acceptance criteria for a "passed" drill

- [ ] Regulator deadline stamp appeared within 1 minute of the incident
      being logged.
- [ ] Generated notification letter was complete and ready to send.
- [ ] Containment steps all ticked within 15 minutes of detection.
- [ ] Status transitions emitted audit rows (verified in `/admin/`).
- [ ] At least 3 action items were captured in the risk register.
- [ ] A timed replay of the drill takes ≤ 90 minutes.

Any failure is a blocker for production readiness. Re-run after fixes.

---

## Sign-off

| Role | Name | Date |
|---|---|---|
| DPO |  |  |
| Engineering lead |  |  |
| Support / Comms |  |  |
