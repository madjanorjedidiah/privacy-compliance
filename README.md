# Privacy Compliance — Free, Self-Hosted Data Protection Platform

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](LICENSE)
[![tests](https://img.shields.io/badge/tests-71%2F71-brightgreen)]()
[![Code of Conduct](https://img.shields.io/badge/code%20of%20conduct-Contributor%20Covenant%20v2.1-blue)](CODE_OF_CONDUCT.md)

> **A free, open-source, self-hosted compliance platform.** Tell it what
> your business does; it tells you exactly which data-protection laws apply
> across Ghana, Kenya, Nigeria, USA, and Europe — track readiness, score
> risk, generate policies, prove accountability.

This project is a gift to SMEs and NGOs that need to comply with data-
protection law but cannot afford commercial compliance suites. There is
no SaaS. There is no paid tier. You deploy it on your own infrastructure
(or a free-tier VPS); you become the data controller for your workspace;
the project maintainers never see your data.

- **Licence:** [AGPL-3.0-or-later](LICENSE) — free to use, modify, and
  redistribute. If you run a modified version as a network service, you
  must share your changes with your users. That is the deal.
- **Contributing:** see [CONTRIBUTING.md](CONTRIBUTING.md).
- **Security:** disclose privately per [SECURITY.md](SECURITY.md).

## What it does

A Django + PostgreSQL application that turns data-protection compliance from a one-off audit into a continuous posture. For any organisation it:

1. **Scopes** which laws apply — GDPR, Ghana DPA 2012, Kenya DPA 2019, Nigeria NDPA 2023, CCPA/CPRA — based on a 3-step profile wizard
2. **Tracks** progress against every obligation with an auditable control register and evidence vault
3. **Scores** risk using a multi-factor engine (likelihood × impact × data sensitivity × volume × regulator activity × control effectiveness)
4. **Shows the gap** — a jurisdictions × control-category heatmap with coverage percentages
5. **Maps across regimes** — crosswalks so "if you've done X under GDPR, here's what's still needed for NDPA"
6. **Generates documents** — Privacy Notices (per jurisdiction), ROPAs, DSAR responses with org-context filled in
7. **Handles subject rights & incidents** — DSAR register with 30-day SLA; incident register with 72-hour regulator deadline

## Business value (CEO view)

| Competitors | Our innovation |
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

The production stack at `mydatacompliance.domainname` **does not run its
own Postgres/Redis/NPM**. Instead it joins the host's existing
`nginx_proxy_manager_default` docker network and talks to:

- `pgbouncer:6432` → shared Postgres (create the `privacy_db` database + role)
- `redis:6379` → shared Redis (use DB indexes 4 for cache, 5 for celery)
- Nginx Proxy Manager → terminates TLS, forwards to `privacy_nginx:80`

Services launched by `docker-compose.yml`:

| Service | Purpose |
|---|---|
| `privacy_django` | gunicorn serving the Django app |
| `privacy_celery` | Celery worker (DPA expiry sweeps, training reminders, ad-hoc jobs) |
| `privacy_beat` | Celery Beat scheduler (DB-backed via `django_celery_beat`) |
| `privacy_nginx` | Internal nginx — static/media + upstream routing, behind NPM |

Deploy steps:

```bash
cp .env.example .env               # fill in APP_SECRET_KEY + POSTGRES_PASSWORD
docker compose build
docker compose up -d
# Point an NPM proxy host from mydatacompliance.domainname → privacy_nginx:80
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

This platform provides compliance management tooling. Content shipped in the catalog and templates is a best-effort paraphrase of public sources and is **not legal advice**. Consult qualified counsel in each jurisdiction before publication.

## Status

MVP walking-skeleton — acceptance-criteria-green, 27/27 tests pass. See `docs/superpowers/specs/2026-04-22-privacy-compliance-design.md` for full scope including deferred items.
