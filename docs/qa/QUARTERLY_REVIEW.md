# Quarterly Compliance & Security Review

A 2-hour meeting every 3 months that keeps the platform's compliance
posture from drifting. Chaired by the DPO; attended by the engineering
lead and an ops representative.

> This is the cadence your auditors will ask for. If you can show a
> signed-off review pack at each quarter end, most ISO 27001 / 27701
> surveillance audits become a paperwork pass.

---

## Inputs (assemble before the meeting)

- [ ] Automated test pass count + trend over the last quarter
- [ ] Production incident log for the quarter (all `Incident` rows with `resolved_at IS NOT NULL`)
- [ ] DSAR metrics table from `DSAR_DRILL.md`
- [ ] Vendor register export — expired or expiring-soon DPAs
- [ ] Training register — users with expired `TrainingRecord`s
- [ ] Risk register — Critical/High risks that have moved
- [ ] Dependency CVE report (`pip-audit` snapshot)
- [ ] Log-aggregator summary — 5xx rate, failed-login spikes
- [ ] List of new or changed sub-processors

---

## Agenda

### 1. Previous-quarter action-item review (10 min)
- [ ] Every action item from the last review is either closed or
      re-opened with a fresh owner and due date.

### 2. Incidents & near-misses (20 min)
- [ ] Walk through every logged incident; confirm the 72-hour
      notification clock was honoured where applicable.
- [ ] Capture near-miss events that did not reach `Incident` status —
      decide whether any of them should become a `Risk` entry.

### 3. DSAR performance (10 min)
- [ ] Median + p95 response time within SLA.
- [ ] Any refusals? Were they documented?

### 4. Vendor & sub-processor lifecycle (15 min)
- [ ] DPAs expiring within 90 days → renewal owner named.
- [ ] Any new sub-processors? If yes, `/cookies/` + privacy notice
      updated and customers notified.
- [ ] TIA still valid for each cross-border transfer?

### 5. Training currency (10 min)
- [ ] Which users have expired `TrainingRecord`s — escalate to
      managers with a refresh deadline.

### 6. Access review (15 min)
- [ ] Dump of all `Membership` rows sorted by role. Confirm:
  - Every Owner is still an employee.
  - No dormant Auditor/Viewer that should be removed.
  - Sole-owner workspaces — consider adding a deputy.
- [ ] Platform admin accounts (`is_staff=True`) audit.

### 7. Secret rotation (5 min)
- [ ] `APP_SECRET_KEY` rotated if last rotation > 12 months ago.
- [ ] Postgres application role password rotated if > 6 months.
- [ ] Any sub-processor tokens rotated per their policy.

### 8. Dependency & image hygiene (10 min)
- [ ] All Critical / High CVEs have a remediation plan or accepted risk.
- [ ] Base images updated (Python, Postgres, Redis, nginx).
- [ ] Container images re-scanned with `trivy image <image>`.

### 9. COMPLIANCE.md spot-check (15 min)

Pick **four rows at random** from `COMPLIANCE.md`'s matrix and verify
the referenced control still exists and functions. Examples:

- "HSTS 1y header" → `curl -sI https://.../` shows the header.
- "`AuthEvent` audit log" → recent rows exist for login / logout.
- "Per-jurisdiction DSAR deadline" → create a California DSAR in
  staging; confirm 45-day due date.

### 10. Risks & follow-ups (10 min)
- [ ] Residual risks in `COMPLIANCE.md §6` — any closed this quarter?
- [ ] New risks to add.
- [ ] Actions with owners + dates for next quarter.

---

## Output artefact

A single PDF saved to `docs/compliance/reviews/{YYYY-QN}-review.pdf`
containing:

1. Meeting minutes
2. Snapshots of the input tables
3. Action-item list with owner + date
4. DPO signature

Link to it from `COMPLIANCE.md` so auditors find it in one hop.

---

## Annual deep-dive (every fourth review)

On the Q4 cycle, add:

- [ ] Full `UAT_SCRIPTS.md` re-run by a rotating tester
- [ ] `INCIDENT_DRILL.md` tabletop
- [ ] `DSAR_DRILL.md` simulation
- [ ] External pen-test report review
- [ ] Privacy-notice + terms review by counsel
- [ ] Renewal of Ghana DPC registration
