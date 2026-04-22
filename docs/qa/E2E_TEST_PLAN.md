# End-to-End Test Plan — Privacy Compliance Platform

This is the master test plan for the Privacy Compliance Platform hosted at
`mydatacompliance.domainname`. It is organised by layer — **Infrastructure**,
**Business logic**, **Management** — and every section lists explicit
acceptance criteria so a reviewer can tick each one off.

> Use this alongside the role-based walk-throughs in `UAT_SCRIPTS.md`, the
> deployment gate in `PRE_DEPLOY_CHECKLIST.md`, and the scheduled drills in
> `INCIDENT_DRILL.md` / `DSAR_DRILL.md`.

---

## Legend

- ✅ automated — covered by `./scripts/verify.sh` or the test suite
- 🔧 scripted — one-shot operator command (copy-paste from here)
- 👤 manual — human-in-the-loop check

---

## 1. Infrastructure layer

### 1.1 Container & network (AgriCircle shared-infra pattern)

| # | Check | How | ✓ |
|---|---|---|---|
| 1.1.1 | All four containers (`privacy_django`, `privacy_celery`, `privacy_beat`, `privacy_nginx`) are `healthy` | 🔧 `docker compose ps` | |
| 1.1.2 | App containers share the external `nginx_proxy_manager_default` network | 🔧 `docker network inspect nginx_proxy_manager_default \| jq '.[].Containers'` — expect all four listed | |
| 1.1.3 | No stray host-port bindings (only NPM exposes 80/443) | 🔧 `docker compose port privacy_django 8000` returns empty | |
| 1.1.4 | Redis is reachable **only** on the private network | 🔧 `docker compose exec privacy_django redis-cli -h redis ping` returns `PONG`; from host, `redis-cli -h <public-ip> ping` fails | |

### 1.2 Database

| # | Check | How | ✓ |
|---|---|---|---|
| 1.2.1 | Migrations apply cleanly on a fresh Postgres | 🔧 `docker compose exec privacy_django python manage.py migrate --plan` — no unapplied | |
| 1.2.2 | Seed data idempotent | 🔧 run `seed_jurisdictions` + `seed_templates` twice; counts unchanged | |
| 1.2.3 | Connection pooled via PgBouncer (port 6432) | 🔧 `docker compose exec privacy_django python -c "from django.db import connection; print(connection.settings_dict['HOST'], connection.settings_dict['PORT'])"` | |
| 1.2.4 | Periodic tasks seeded | 🔧 `python manage.py shell -c "from django_celery_beat.models import PeriodicTask; print(list(PeriodicTask.objects.values_list('name','task')))"` — expect 2 tasks | |
| 1.2.5 | Backups on schedule with tested restore | 👤 operator policy |  |

### 1.3 Security headers (live)

| # | Check | How | ✓ |
|---|---|---|---|
| 1.3.1 | HSTS 1-year header present | 🔧 `curl -sI https://mydatacompliance.domainname/ \| grep -i strict-transport` | |
| 1.3.2 | CSP header present with `default-src 'self'`, `frame-ancestors 'none'` | 🔧 `curl -sI https://mydatacompliance.domainname/accounts/login/ \| grep -i content-security-policy` | |
| 1.3.3 | `X-Frame-Options: DENY` | 🔧 same curl | |
| 1.3.4 | `X-Content-Type-Options: nosniff` | 🔧 same curl | |
| 1.3.5 | `Referrer-Policy: same-origin` | 🔧 same curl | |
| 1.3.6 | Secure + HttpOnly session cookie after login | 🔧 `curl -siXPOST --data 'username=...&password=...' /accounts/login/` — check `Set-Cookie` flags | |
| 1.3.7 | CSRF token required on every unsafe method | 👤 try a POST without token → 403 | |

### 1.4 Rate limiting & lockout

| # | Check | How | ✓ |
|---|---|---|---|
| 1.4.1 | 5 bad logins within 1h lock the account | 🔧 bash loop: `for i in 1..6; do curl --data 'username=demo&password=wrong' /accounts/login/; done` — 6th returns the lockout page (429 / template) | |
| 1.4.2 | Rate limit keyed on real client IP (X-Forwarded-For) | 🔧 send 20 requests with distinct `X-Forwarded-For` values → none blocked (independent IPs) | |
| 1.4.3 | Redis is the rate-limit backend in prod (no `LocMem` warning in `privacy_django` startup) | 🔧 `docker compose logs privacy_django \| grep -i 'APP_SECRET_KEY is set'` — must be empty | |

### 1.5 Observability

| # | Check | How | ✓ |
|---|---|---|---|
| 1.5.1 | `/ops/health/` returns 200 JSON | 🔧 `curl /ops/health/` | |
| 1.5.2 | `/ops/readyz/` returns 200 when DB + cache OK | 🔧 `curl /ops/readyz/` | |
| 1.5.3 | Every response carries an `X-Request-ID` header and the same ID appears in JSON logs | 🔧 capture request ID from response; grep container logs for it | |
| 1.5.4 | Celery Beat schedule is firing | 🔧 `docker compose logs privacy_celery \| grep 'flag_expiring_dpas'` after 24h | |

---

## 2. Business-logic layer

### 2.1 Onboarding + applicability engine

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.1.1 | New signup → 3-step wizard completes in < 2 min on a fresh browser | |
| 2.1.2 | Kudu Fintech profile (GH + EU subjects, CA offer, 250k subjects) resolves to: GDPR, Ghana DPA, Kenya DPA (if KE chosen), NDPA (if NG chosen), CCPA | |
| 2.1.3 | Removing EU/California from the profile and re-running the assessment marks old controls NOT_APPLICABLE (or deletes them if untouched) — **zombie check** | |
| 2.1.4 | The applicability rationale appears on every applicable-framework row | |

Automated by: ✅ `jurisdictions.tests`, ✅ `assessments.tests`.

### 2.2 Compliance workflow + scoring

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.2.1 | Fresh workspace shows a 0% compliance score | |
| 2.2.2 | Clicking a requirement from `Not started` → `In progress` → `Implemented` moves the jurisdiction score and the global score monotonically upward | |
| 2.2.3 | Score is **severity-weighted** — implementing a severity-5 GDPR Art. 33 bumps the score more than a severity-2 cookie item | |
| 2.2.4 | Every transition emits exactly one `ControlStatusChange` row | |
| 2.2.5 | Gap Map colour grading: <30% red, 30-59% amber, 60-79% lime, ≥80% emerald | |

Automated by: ✅ `dashboard.tests.DashboardServiceTests.test_weighted_score_rises_as_controls_implemented`, ✅ `test_quick_status_emits_audit_log`.

### 2.3 DPO-grade registers

| Register | Acceptance criterion | ✓ |
|---|---|---|
| ROPA | Creating a processing activity in org A is invisible to org B (detail + edit → 404) | |
| ROPA | Form dropdowns never show another org's users or retention policies | |
| Retention | Legal-hold flag suppresses the destruction countdown in list view | |
| Training | Record saved without explicit `expires_on` auto-computes from module refresh window | |
| Training | Expired records render `badge-danger Expired` | |
| DPIA | ≥2 trigger boxes fires the `DPIA required` badge | |
| Vendors | DPA expiring within 60 days turns the row amber; past expiry turns it rose | |

Automated by: ✅ `accounts.test_isolation.DPORegisterIsolationTests`, ✅ `vendors.tests`, ✅ `training.tests`, ✅ `dpia.tests`.

### 2.4 Template engine

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.4.1 | Generating the Ghana Privacy Notice produces markdown containing the org's name, "Act 843", "Data Protection Commission" | |
| 2.4.2 | Universal ROPA template links to requirement codes across GH + KE + NG + GDPR | |
| 2.4.3 | `/templates/` page groups templates by jurisdiction card | |
| 2.4.4 | "Use template" button on a compliance row jumps the user directly to the filled document | |

Automated by: ✅ `templates_engine.tests`.

### 2.5 DSAR + incidents

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.5.1 | DSAR due date = received-at + 30 days for GDPR / KE / GH / NG subjects, + 45 days for `US-CA` | |
| 2.5.2 | Incident detected-at → 72h default deadline; `affected_jurisdictions` shorter windows pull the deadline earlier | |
| 2.5.3 | Overdue DSAR row shows `Overdue` badge | |

### 2.6 Multi-tenant isolation (security-critical business rule)

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.6.1 | User in org A cannot GET/POST any URL of org B's resources — every path returns 404 | |
| 2.6.2 | Form `<select>` options never leak another org's users, retention policies, DPIAs | |
| 2.6.3 | Dashboard KPIs never mix numbers from another org | |

Automated by: ✅ `accounts.test_isolation` (9 tests).

### 2.7 RBAC

| Role | Expected capability | ✓ |
|---|---|---|
| Owner | Full read/write everywhere | |
| DPO | Full read/write | |
| Compliance | Full read/write | |
| Auditor | Read-only; POST → 403 | |
| Viewer | Read-only; POST → 403 | |

Automated by: ✅ `accounts.test_isolation.RoleEnforcementTests`.

### 2.8 Self-service data rights

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.8.1 | `POST /accounts/me/export/` returns a downloadable JSON with user + memberships + auth events | |
| 2.8.2 | Sole org owner cannot self-delete (blocked with explanatory message) | |
| 2.8.3 | Co-owned user who confirms their username is erased; account record gone, `ACCOUNT_DELETE` audit row present | |
| 2.8.4 | Every data-subject action writes an `AuthEvent` | |

Automated by: ✅ `accounts.test_privacy_pages`.

### 2.9 Background jobs (Celery)

| # | Acceptance criterion | ✓ |
|---|---|---|
| 2.9.1 | `flag_expiring_dpas` scheduled daily and returns `{expired, expiring_soon, missing_dpa}` | |
| 2.9.2 | `flag_expiring_training` scheduled daily | |
| 2.9.3 | Worker + beat auto-restart on Redis reconnect | |

---

## 3. Management layer

### 3.1 Governance documentation

| # | Artefact | Owner | ✓ |
|---|---|---|---|
| 3.1.1 | `COMPLIANCE.md` reviewed by counsel | DPO | |
| 3.1.2 | `GO_LIVE.md` every box ticked | Ops + DPO | |
| 3.1.3 | Sub-processor list published | Legal | |
| 3.1.4 | DPA template ready for customer signature | Legal | |
| 3.1.5 | Operator's own DPIA in `docs/compliance/` | DPO | |

### 3.2 Role definitions & onboarding

| # | Acceptance criterion | ✓ |
|---|---|---|
| 3.2.1 | Every role in `Membership.Role` has a documented responsibility | |
| 3.2.2 | DPO has both primary and deputy contacts filed with the DPC | |
| 3.2.3 | Admin access is restricted (IP allowlist or MFA) | |
| 3.2.4 | Secret rotation runbook signed off | |

### 3.3 Incident readiness

| # | Acceptance criterion | ✓ |
|---|---|---|
| 3.3.1 | Tabletop incident drill (see `INCIDENT_DRILL.md`) completed within 90 days of launch | |
| 3.3.2 | Pre-drafted regulator notification letter on file | |
| 3.3.3 | On-call rotation published and reviewed monthly | |

### 3.4 DSAR readiness

| # | Acceptance criterion | ✓ |
|---|---|---|
| 3.4.1 | `privacy@privacy.domain` inbox monitored within business hours | |
| 3.4.2 | DSAR drill completed (see `DSAR_DRILL.md`) | |
| 3.4.3 | Response templates per request type signed off | |

### 3.5 Supplier lifecycle

| # | Acceptance criterion | ✓ |
|---|---|---|
| 3.5.1 | Every vendor in the platform has an `dpa_on_file=True`, a `dpa_expires_on` ≤ 12 months out, and a `last_security_audit` ≤ 24 months out | |
| 3.5.2 | Vendor review schedule queued in ops calendar | |

### 3.6 Quarterly review

See `QUARTERLY_REVIEW.md` — exec that quarterly and carry forward the
results into the compliance register.

---

## Runtime commands quick-reference

```bash
# Full automated suite
./scripts/verify.sh                     # or ./scripts/verify.sh https://mydatacompliance.domainname

# Django-only tests
docker compose exec privacy_django python manage.py test

# Deploy check
docker compose exec privacy_django python manage.py check --deploy

# One-shot live smoke
curl -fsS https://mydatacompliance.domainname/ops/health/
curl -fsS https://mydatacompliance.domainname/ops/readyz/

# Container status
docker compose ps && docker compose logs --since 1h --tail 50
```

---

## Sign-off

| Layer | Reviewer | Date | Notes |
|---|---|---|---|
| Infrastructure | SRE / Ops Lead |  |  |
| Business logic | Staff Engineer |  |  |
| Management | DPO + Counsel |  |  |

All three signatures required to pass this gate before a customer-facing deploy.
