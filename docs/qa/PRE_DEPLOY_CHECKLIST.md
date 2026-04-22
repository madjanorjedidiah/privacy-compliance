# Pre-Deploy Checklist

Run this every time before promoting a build to `mydataprotection.cocoatool.org`.
The goal is to stop anything that will blow up production — nothing more, nothing less.

> Fastest path: `./scripts/verify.sh https://staging.cocoatool.org` captures
> the bulk of this. The boxes below are the human decisions still required.

---

## 1. Code gate (automated — block merge if red)

- [ ] `./scripts/verify.sh` exits 0 on the PR branch
- [ ] CI reports 0 failing tests
- [ ] `pip-audit` reports no Critical/High CVEs
- [ ] No new `.env` files or secrets in the diff (`git diff --name-only` clean)
- [ ] Migrations are linear (`manage.py makemigrations --check --dry-run` returns exit 0)
- [ ] `manage.py check --deploy` passes with `DJANGO_DEBUG=0 APP_SECRET_KEY=<test-value>`

## 2. Staging gate (run against the staging URL)

- [ ] `./scripts/verify.sh https://staging.cocoatool.org` exits 0
- [ ] Live smoke passes: `curl -fsS https://staging.cocoatool.org/ops/health/` returns `alive`
- [ ] Security headers present (HSTS / CSP / X-Frame-Options / X-Content-Type-Options / Referrer-Policy)
- [ ] A fresh signup → onboarding → compliance click-through works end-to-end
- [ ] Celery worker + beat are `healthy` and Beat is ticking (inspect logs for scheduled task runs)
- [ ] A deliberate bad login shows the rate-limit page after 5 attempts (django-axes)

## 3. Data gate (prod DB)

- [ ] Last backup < 24h old and the restore was verified this month
- [ ] New migrations reviewed for locking behaviour (no `ALTER TABLE` on large
      tables without `CONCURRENTLY`; no implicit column rewrites)
- [ ] Expected backfill scripts queued with an owner assigned
- [ ] Index additions will be concurrent (`--concurrent`) or the table is small enough

## 4. Config gate

- [ ] `.env` on the target host sets `APP_SECRET_KEY` to a strong new value (not the dev default)
- [ ] `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS` all set
- [ ] `REDIS_URL` points at the shared redis; the rate-limit fallback warning is absent from startup logs
- [ ] Postgres credentials rotated from any example defaults
- [ ] `DJANGO_SUPERUSER_*` — bootstrap account with a one-use password; schedule its removal inside 24h

## 5. Observability gate

- [ ] Log shipper is configured for all four containers
- [ ] Alert on `5xx_rate > 1%` for 5 minutes
- [ ] Alert on failed-login > 20/min (possible credential stuffing)
- [ ] Alert on Celery Beat lateness > 10 min
- [ ] Uptime probe from outside the data-centre hitting `/ops/health/`

## 6. Governance gate (operator-side)

- [ ] Change log entry written (what's deploying, why, rollback plan)
- [ ] On-call engineer named for the deploy window
- [ ] If a schema migration is included — rollback script rehearsed on staging
- [ ] Customer-facing change requires a privacy-notice review before release
- [ ] If any cookie / tracker / sub-processor changes — update `/cookies/` + sub-processor list

## 7. Rollback readiness

- [ ] Previous image tag recorded: `docker image inspect privacy_django --format '{{.Id}} {{.RepoTags}}'`
- [ ] `docker compose down && docker compose up -d` confirmed to work against the previous tag
- [ ] DB rollback SQL (or "no-op") filed alongside the migration PR

---

## Deploy command block

```bash
# From the host
git pull
docker compose pull      # if using a registry
docker compose build
docker compose up -d privacy_django privacy_celery privacy_beat privacy_nginx
docker compose exec privacy_django python manage.py migrate --noinput
docker compose exec privacy_django python manage.py setup_periodic_tasks
docker compose exec privacy_django python manage.py check --deploy
curl -fsS https://mydataprotection.cocoatool.org/ops/health/
```

If the `curl` returns a non-200, roll back:

```bash
docker compose down
git checkout <previous-tag>
docker compose up -d
```

---

## Sign-off

| Gate | Approver | Timestamp |
|---|---|---|
| Code | Tech lead |  |
| Staging | QA |  |
| Data | DBA / SRE |  |
| Config | SRE |  |
| Observability | SRE |  |
| Governance | DPO |  |

All six required.
