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

## Deploy — standalone (the easy path)

A single command brings up everything the platform needs — its own
Postgres, Redis, Django + gunicorn, Celery worker, Celery Beat, and
nginx with TLS termination:

```bash
./scripts/quickstart.sh mydomain.example.com
# or just: ./scripts/quickstart.sh   (uses localhost)
```

That script:

1. copies `.env.example` → `.env` and generates a strong `APP_SECRET_KEY`
   + `POSTGRES_PASSWORD` for you;
2. drops a self-signed TLS cert into `deploy/certs/`;
3. runs `docker compose up -d --build`.

Once the `web` container is healthy (~30s, while it runs migrations,
seeds jurisdictions + templates, and schedules periodic tasks), visit:

- `https://localhost/` (accept the self-signed cert warning)
- `https://localhost/admin/`
- `https://localhost/ops/health/`

Services launched:

| Service | Purpose |
|---|---|
| `db` | Postgres 16 (own volume) |
| `redis` | Redis 7 (own volume, AOF) |
| `web` | Django + gunicorn |
| `celery` | Background worker |
| `beat` | Periodic-task scheduler |
| `nginx` | TLS terminator + static / media + reverse proxy |

### Production TLS — Let's Encrypt

Once DNS points at the host and ports 80 / 443 are open:

```bash
# In .env
CERTBOT_DOMAIN=mydatacompliance.example.com
CERTBOT_EMAIL=ops@privacy.domain

# Obtain + auto-renew
docker compose --profile letsencrypt up -d certbot
docker compose restart nginx
```

Certbot runs forever in the background, renewing every 12h through the
nginx `/.well-known/acme-challenge/` webroot.

### Deploy — shared infra (advanced)

If you already run shared Postgres / Redis / Nginx Proxy Manager on the
host, use the alternative compose instead:

```bash
docker compose -f docker-compose.shared.yml up -d
```

See the docstring at the top of
[`docker-compose.shared.yml`](docker-compose.shared.yml) for the network
and service names it expects.

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
