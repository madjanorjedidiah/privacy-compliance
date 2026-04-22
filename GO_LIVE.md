# Go-Live Checklist — deploying-organisation's edition

Work every item in this list before opening your instance of the platform
to real users. Tick the box when closed.

> **This checklist is for you — the organisation installing and running the
> platform.** You are the Data Controller of your workspace. The project
> maintainers ship the code and never see your data; they do not perform
> these steps for you. If you later decide to run a shared multi-tenant
> hosted instance for other organisations, revisit every item with counsel
> — a hosted service has a higher regulatory bar than a self-hosted tool.

## 1. Legal & regulatory

- [ ] **Ghana DPC registration** — the operating company is registered as a
  Data Controller with the Ghana Data Protection Commission
  (<https://dataprotection.org.gh/>). Certificate number recorded here: `____`.
  Renewal date calendared.
- [ ] **DPO named** — primary + deputy. Contacts published in `/privacy/` and
  filed with the DPC.
- [ ] **Privacy notice** at `/privacy/` reviewed by counsel.
- [ ] **Terms of service** at `/terms/` reviewed by counsel.
- [ ] **Sub-processor list** published or available on request.
- [ ] **Data Processing Agreement** signed with each paying customer.
- [ ] **Transfer Impact Assessment (TIA)** on file for any cross-border flow
  (hosting, email, monitoring).
- [ ] **Operator's own DPIA** stored in `docs/compliance/` — internal use only.

## 2. Production environment configuration

Environment variables (populate a `.env` from `.env.example`):

- [ ] `DJANGO_DEBUG=0` on the container.
- [ ] `APP_SECRET_KEY` — 64-byte random, unique to prod.
  Generate: `python -c "import secrets; print(secrets.token_urlsafe(64))"`
- [ ] `DJANGO_ALLOWED_HOSTS=mydataprotection.cocoatool.org,privacy_django,privacy_nginx`
- [ ] `DJANGO_CSRF_TRUSTED_ORIGINS=https://mydataprotection.cocoatool.org`
- [ ] `DATABASE_URL` or `DB_*` — points at shared Postgres via `pgbouncer:6432`.
  Dedicated database `privacy_db` + dedicated role with only the rights it needs.
- [ ] `REDIS_URL=redis://redis:6379/4` — rate-limit counters live here.
- [ ] `CELERY_BROKER_URL=redis://redis:6379/5`
- [ ] `APP_ENABLE_HTTPS=1`, `APP_HSTS_SECONDS=31536000`
- [ ] `DJANGO_SUPERUSER_*` — bootstrap a bootstrap account, then rotate it
  (create a real Owner through signup and delete the bootstrap account).

Infrastructure:

- [ ] Postgres backups — nightly, off-site, encrypted at rest, tested restore.
- [ ] NPM proxy host → `privacy_nginx:80` with Let's Encrypt TLS.
- [ ] HSTS preload (only after you're certain the cert is stable).
- [ ] Redis is **not** exposed publicly.
- [ ] Firewall rules audited — only 80/443 inbound.

## 3. Application bootstrap

Once containers are up:

```bash
docker compose exec privacy_django python manage.py migrate
docker compose exec privacy_django python manage.py seed_jurisdictions
docker compose exec privacy_django python manage.py seed_templates
docker compose exec privacy_django python manage.py setup_periodic_tasks
docker compose exec privacy_django python manage.py createsuperuser
```

- [ ] Periodic tasks registered (`Nightly DPA expiry sweep`,
  `Nightly training expiry sweep`). Check `/admin/django_celery_beat/`.
- [ ] Celery Beat + worker containers show `ready` in logs.

## 4. Security verification

- [ ] `curl -I https://mydataprotection.cocoatool.org` returns
  `Strict-Transport-Security`, `Content-Security-Policy`, and
  `X-Frame-Options: DENY`.
- [ ] Failed-login flood test — `django-axes` locks the account at 5 attempts.
- [ ] CSRF token enforced on all POSTs (spot check with curl without token).
- [ ] Admin `/admin/` is either IP-restricted or behind an additional factor.
- [ ] `/ops/health/` and `/ops/readyz/` return JSON 200.
- [ ] Static + media URLs only serve whitelisted extensions.

## 5. Monitoring & observability

- [ ] Structured JSON logs shipped to your log aggregator.
- [ ] Alert on 5xx rate, on failed-login spike, on Celery Beat stall.
- [ ] Uptime probe against `/ops/health/` every minute.
- [ ] Backup restore test scheduled quarterly.

## 6. Data-subject-request readiness

- [ ] Inbox for `privacy@cocoatool.org` monitored by the DPO.
- [ ] Internal DSAR runbook tested against the seeded DSAR workflow.
- [ ] 30-day SLA clock documented in ticketing.

## 7. Supplier due diligence

For every vendor the operator relies on (hosting, email, monitoring, CDN):

- [ ] DPA signed and filed.
- [ ] ISO 27001 / SOC 2 report on file.
- [ ] Sub-processor list from the vendor reviewed.
- [ ] Reviewed annually.

## 8. Incident response

- [ ] Breach playbook published with on-call rotation.
- [ ] Pre-drafted DPC breach notification letter (use the generated template).
- [ ] Tabletop exercise completed within 90 days of launch.

## 9. First-customer launch gate

- [ ] Pen-test (internal or third-party) completed and remediated.
- [ ] All critical + high items in `COMPLIANCE.md §6 residual risks` have
  either been closed or accepted in writing by the customer.
- [ ] Customer's contract cross-references the signed DPA.
- [ ] Support process — business-hours email + 48h response target — advertised.

Once every box is ticked, flip the DNS.
