#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# quickstart.sh — one command to stand up a fresh standalone instance.
#
# Does exactly three things:
#   1. If `.env` doesn't exist, write one from `.env.example` with a
#      freshly-generated APP_SECRET_KEY and POSTGRES_PASSWORD.
#   2. Generate a self-signed TLS cert in `deploy/certs/` if none exists.
#   3. `docker compose up -d --build`.
#
# Safe to re-run. Won't overwrite an existing `.env` or cert.
#
# Usage:
#   ./scripts/quickstart.sh                       # CN = localhost
#   ./scripts/quickstart.sh mydatacompliance.com  # CN = your domain
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$HERE"

DOMAIN="${1:-localhost}"

# ─── 1. .env ────────────────────────────────────────────────────────────
if [[ -f .env ]]; then
  echo "✓ .env already present — leaving alone."
else
  [[ -f .env.example ]] || { echo "✗ .env.example missing"; exit 1; }
  echo "── Generating .env from .env.example ──"
  cp .env.example .env

  # Generate a strong APP_SECRET_KEY and DB password. Prefer python, fall
  # back to openssl if python isn't on the host path (docker-only install).
  gen() {
    if command -v python3 >/dev/null 2>&1; then
      python3 -c "import secrets; print(secrets.token_urlsafe($1))"
    else
      openssl rand -base64 $1 | tr -d '\n' | tr '+/' '-_' | head -c $(( $1 * 4 / 3 ))
    fi
  }
  SECRET_KEY=$(gen 64)
  DB_PW=$(gen 24)

  # In-place edit (portable sed: write a temp file).
  sed \
    -e "s|replace-me-with-a-64-byte-random-value|$SECRET_KEY|" \
    -e "s|POSTGRES_PASSWORD=change-me|POSTGRES_PASSWORD=$DB_PW|" \
    -e "s|DJANGO_ALLOWED_HOSTS=mydatacompliance.domainname,|DJANGO_ALLOWED_HOSTS=$DOMAIN,localhost,127.0.0.1,|" \
    -e "s|DJANGO_CSRF_TRUSTED_ORIGINS=https://mydatacompliance.domainname|DJANGO_CSRF_TRUSTED_ORIGINS=https://$DOMAIN|" \
    .env > .env.tmp && mv .env.tmp .env
  chmod 600 .env
  echo "✓ .env written (chmod 600) with a generated APP_SECRET_KEY + POSTGRES_PASSWORD."
fi

# ─── 2. TLS cert ────────────────────────────────────────────────────────
"$HERE/scripts/init-standalone.sh" "$DOMAIN"

# ─── 3. docker compose up ───────────────────────────────────────────────
echo "── docker compose up -d --build ──"
docker compose up -d --build

echo
echo "✓ Privacy Compliance is starting. Follow logs with:"
echo "    docker compose logs -f web"
echo
echo "First-boot bootstrap (migrations, seeds, periodic tasks) runs inside"
echo "the web container and takes ~30 seconds. Then visit:"
echo
echo "    https://localhost/              (self-signed; accept the warning)"
echo
echo "Admin URL:"
echo "    https://localhost/admin/"
