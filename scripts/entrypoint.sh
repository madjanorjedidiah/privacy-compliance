#!/usr/bin/env bash
set -euo pipefail

cd /app

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-privacy_compliance.settings}"

echo "[entrypoint] settings=${DJANGO_SETTINGS_MODULE} DEBUG=${DJANGO_DEBUG:-unset}"

# Only run DB-mutating startup work on the "primary" container (the web
# server). Celery worker + beat containers should NOT also run migrations —
# they race each other and slow startup. Control via BOOTSTRAP env.
if [[ "${BOOTSTRAP:-0}" == "1" ]]; then
  echo "[entrypoint] applying migrations…"
  python manage.py migrate --noinput

  echo "[entrypoint] collecting static…"
  python manage.py collectstatic --noinput > /dev/null

  if [[ "${AUTO_SEED:-1}" == "1" ]]; then
    echo "[entrypoint] seeding jurisdictions, templates, periodic tasks…"
    python manage.py seed_jurisdictions || true
    python manage.py seed_templates || true
    python manage.py setup_periodic_tasks || true
  fi

  if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
    echo "[entrypoint] ensuring superuser ${DJANGO_SUPERUSER_USERNAME}…"
    python manage.py createsuperuser --noinput || true
  fi
fi

echo "[entrypoint] starting: $*"
exec "$@"
