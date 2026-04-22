# QA & Verification Pack

Everything a reviewer needs to believe the platform is production-ready —
automated, scripted, and human.

| Layer | Document | Owner | Cadence |
|---|---|---|---|
| **Automated** | `scripts/verify.sh` runs tests + `check --deploy` + optional live-smoke | Engineering | every commit / PR / staging |
| Automated | [`E2E_TEST_PLAN.md`](E2E_TEST_PLAN.md) — master plan with Infra / Business / Management acceptance criteria | Staff Engineer + DPO | before every major release |
| Scripted | [`PRE_DEPLOY_CHECKLIST.md`](PRE_DEPLOY_CHECKLIST.md) — one page of must-dos before flipping a deploy | SRE | every deploy |
| Scripted | [`UAT_SCRIPTS.md`](UAT_SCRIPTS.md) — 5 role-based walk-throughs | QA | pre-release + quarterly |
| Manual | [`INCIDENT_DRILL.md`](INCIDENT_DRILL.md) — 90-minute tabletop exercising the 72-hour breach loop | DPO | quarterly + within 90d of go-live |
| Manual | [`DSAR_DRILL.md`](DSAR_DRILL.md) — end-to-end data-subject-request simulation | DPO + Compliance | 6-monthly |
| Manual | [`QUARTERLY_REVIEW.md`](QUARTERLY_REVIEW.md) — 2-hour governance meeting cadence | DPO (chair) | every 3 months |

## How the pack maps to standards

- **ISO 27001 A.5.31-34** — compliance review: `QUARTERLY_REVIEW.md` §9
- **ISO 27701 PIMS control review** — `QUARTERLY_REVIEW.md`
- **GDPR Art. 33 / Ghana DPA s.43 readiness** — `INCIDENT_DRILL.md`
- **GDPR Arts. 15-22 operational readiness** — `DSAR_DRILL.md`
- **SOC 2 CC4 monitoring activities** — `QUARTERLY_REVIEW.md` + `PRE_DEPLOY_CHECKLIST.md` observability section
- **OWASP ASVS V4 access control** — `UAT_SCRIPTS.md` (Auditor / Viewer scripts)

## Running the pack

```bash
# Single command — full automated layer
./scripts/verify.sh

# Same but probing a live instance
./scripts/verify.sh https://mydatacompliance.domainname

# Manual scripts — work through the markdown, tick boxes as you go,
# and save the completed doc under docs/qa/runs/YYYY-QN/.
```
