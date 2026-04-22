# Sentinel — Multi-Jurisdictional Data Protection Compliance Platform

> Tell us what your business does; we tell you exactly which data-protection laws apply across Ghana, Kenya, Nigeria, USA and Europe — track readiness, score risk, generate policies.

## What it does

Sentinel is a Django + PostgreSQL/SQLite application that turns data-protection compliance from a one-off audit into a continuous posture. For any organisation it:

1. **Scopes** which laws apply — GDPR, Ghana DPA 2012, Kenya DPA 2019, Nigeria NDPA 2023, CCPA/CPRA — based on a 3-step profile wizard
2. **Tracks** progress against every obligation with an auditable control register and evidence vault
3. **Scores** risk using a multi-factor engine (likelihood × impact × data sensitivity × volume × regulator activity × control effectiveness)
4. **Shows the gap** — a jurisdictions × control-category heatmap with coverage percentages
5. **Maps across regimes** — crosswalks so "if you've done X under GDPR, here's what's still needed for NDPA"
6. **Generates documents** — Privacy Notices (per jurisdiction), ROPAs, DSAR responses with org-context filled in
7. **Handles subject rights & incidents** — DSAR register with 30-day SLA; incident register with 72-hour regulator deadline

## Business value (CEO view)

| Competitors | Sentinel's innovation |
|---|---|
| Static checklists | Dynamic jurisdiction router — only what applies to you |
| Generic templates | Contextual template engine — filled from your org profile |
| Siloed country views | Cross-jurisdictional gap map |
| One-off audits | Living risk score + evidence vault |

## Tech stack

- Django 5.1 + Django REST Framework
- SQLite (dev) / PostgreSQL (prod-ready)
- Server-rendered Django templates + Tailwind CSS + HTMX + Alpine.js
- Whitenoise for static files
- Celery + Redis scaffolding for async notifications (stubbed in MVP)

## Quickstart — local (SQLite)

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jurisdictions
.venv/bin/python manage.py seed_templates
.venv/bin/python manage.py createsuperuser
.venv/bin/python manage.py runserver
```

Visit http://127.0.0.1:8000/ — sign up, walk the onboarding wizard, and land on the Command Center.

## Deploy — shared infra (Nginx Proxy Manager + Postgres + Redis)

The production stack at `mydataprotection.cocoatool.org` **does not run its
own Postgres/Redis/NPM**. Instead it joins the host's existing
`nginx_proxy_manager_default` docker network and talks to:

- `pgbouncer:6432` → shared Postgres (create the `privacy_db` database + role)
- `redis:6379` → shared Redis (use DB indexes 4 for cache, 5 for celery)
- Nginx Proxy Manager → terminates TLS, forwards to `privacy_nginx:80`

Services launched by `docker-compose.yml`:

| Service | Purpose |
|---|---|
| `privacy_django` | gunicorn serving the Sentinel Django app |
| `privacy_celery` | Celery worker (DPA expiry sweeps, training reminders, ad-hoc jobs) |
| `privacy_beat` | Celery Beat scheduler (DB-backed via `django_celery_beat`) |
| `privacy_nginx` | Internal nginx — static/media + upstream routing, behind NPM |

Deploy steps:

```bash
cp .env.example .env               # fill in SENTINEL_SECRET_KEY + POSTGRES_PASSWORD
docker compose build
docker compose up -d
# Point an NPM proxy host from mydataprotection.cocoatool.org → privacy_nginx:80
```

The `privacy_django` command handles migrations, idempotent seeds, static
collection, and (optionally) superuser provisioning on startup.

## Testing

```bash
.venv/bin/python manage.py test
```

27 tests cover the applicability engine, crosswalk, risk scoring, template rendering, assessment flow, dashboard services, and smoke tests for every major view.

## Layout

```
privacy_compliance/  project settings + root URL config (matches repo name — find config by parent folder)
core/                shared utilities (TimeStampedModel, choices, context processors)
accounts/            Organization, User, Membership, OrgProfile + onboarding wizard
jurisdictions/       Jurisdiction, Framework, Requirement, crosswalk, applicability engine + seed data
assessments/         Applicability results, run_assessment service
controls/            Control register, evidence, HTMX status updates
risks/               Risk register with scoring engine and heatmap
templates_engine/    Jurisdiction-aware policy template engine (Privacy Notice, ROPA, DSAR)
dsar/                Data subject request intake
incidents/           Breach register with 72-hour deadlines
vendors/             Sub-processor register (MVP model only)
dashboard/           Executive KPIs, gap map, maturity-per-framework
templates/           Base + app templates (Tailwind)
static/css/app.css   Component styles layered on Tailwind
docs/superpowers/specs/2026-04-22-privacy-compliance-design.md  Design spec
.gstack/qa-reports/  QA reports from the investigate + qa skill passes
```

## Legal disclaimer

Sentinel provides compliance management tooling. Content shipped in the catalog and templates is a best-effort paraphrase of public sources and is **not legal advice**. Consult qualified counsel in each jurisdiction before publication.

## Status

MVP walking-skeleton — acceptance-criteria-green, 27/27 tests pass. See `docs/superpowers/specs/2026-04-22-privacy-compliance-design.md` for full scope including deferred items.
