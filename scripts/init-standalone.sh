#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# init-standalone.sh — prepare `deploy/certs/` for a standalone deploy.
#
# Generates a self-signed TLS cert (2048-bit RSA, 398 days = Apple/Safari
# max) if no fullchain.pem is present yet. Safe to re-run; won't overwrite.
#
# Usage:
#   ./scripts/init-standalone.sh                       # cert CN = localhost
#   ./scripts/init-standalone.sh mydatacompliance.com  # cert CN = your domain
#
# For production — replace the self-signed cert with a Let's Encrypt one
# using the compose `letsencrypt` profile. See README.md.
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
CERT_DIR="$HERE/deploy/certs"
DOMAIN="${1:-localhost}"

mkdir -p "$CERT_DIR"

FULLCHAIN="$CERT_DIR/fullchain.pem"
PRIVKEY="$CERT_DIR/privkey.pem"

if [[ -s "$FULLCHAIN" && -s "$PRIVKEY" ]]; then
  echo "✓ TLS cert already present at $CERT_DIR — leaving alone."
  exit 0
fi

command -v openssl >/dev/null 2>&1 || {
  echo "✗ openssl not found — install it or provide your own cert at $CERT_DIR" >&2
  exit 1
}

echo "── Generating self-signed cert for $DOMAIN ──"
openssl req -x509 -newkey rsa:2048 -sha256 -nodes \
  -keyout "$PRIVKEY" \
  -out "$FULLCHAIN" \
  -days 398 \
  -subj "/CN=$DOMAIN" \
  -addext "subjectAltName=DNS:$DOMAIN,DNS:localhost,IP:127.0.0.1"

chmod 600 "$PRIVKEY"
chmod 644 "$FULLCHAIN"

echo "✓ Self-signed cert written to $CERT_DIR"
echo "  fullchain.pem   ($(wc -c < "$FULLCHAIN") bytes)"
echo "  privkey.pem     ($(wc -c < "$PRIVKEY") bytes)"
echo
echo "Browsers will show a TLS warning for this cert — that's expected."
echo "For production, swap in a Let's Encrypt cert:"
echo "  export CERTBOT_DOMAIN=$DOMAIN CERTBOT_EMAIL=ops@example.com"
echo "  docker compose --profile letsencrypt up -d certbot"
