#!/usr/bin/env bash
set -euo pipefail

cd /app

export DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS_MODULE:-privacy_compliance.settings}"

echo "[entrypoint] django env=${DJANGO_ENV:-unset} settings=${DJANGO_SETTINGS_MODULE}"

echo "[entrypoint] applying migrations…"
python manage.py migrate --noinput

echo "[entrypoint] collecting static…"
python manage.py collectstatic --noinput > /dev/null

if [[ "${AUTO_SEED:-1}" == "1" ]]; then
  echo "[entrypoint] seeding jurisdictions & templates…"
  python manage.py seed_jurisdictions || true
  python manage.py seed_templates || true
fi

if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" && -n "${DJANGO_SUPERUSER_PASSWORD:-}" && -n "${DJANGO_SUPERUSER_EMAIL:-}" ]]; then
  echo "[entrypoint] ensuring superuser ${DJANGO_SUPERUSER_USERNAME}…"
  python manage.py createsuperuser --noinput || true
fi

echo "[entrypoint] starting: $*"
exec "$@"
