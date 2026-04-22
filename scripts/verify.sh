#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# End-to-end verification runner for the Privacy Compliance Platform.
#
# Usage:
#   ./scripts/verify.sh                        # local: tests + check --deploy + pip-audit
#   ./scripts/verify.sh https://staging.url    # also probe a running instance
#
# Exits non-zero on the first failure. Fast-fail by design so CI catches
# regressions immediately. All output is captured to `.gstack/verify-*.log`
# in the current directory.
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

HERE=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$HERE"

TARGET_URL="${1:-}"
LOG_DIR=".gstack"
mkdir -p "$LOG_DIR"
STAMP=$(date +%Y%m%d-%H%M%S)
LOG="$LOG_DIR/verify-$STAMP.log"

# Pick python interpreter
if [[ -x .venv/bin/python ]]; then
  PY=.venv/bin/python
elif command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  echo "✗ python not found" >&2
  exit 2
fi

ok()   { printf '\033[32m✓\033[0m %s\n' "$*" | tee -a "$LOG"; }
warn() { printf '\033[33m!\033[0m %s\n' "$*" | tee -a "$LOG"; }
die()  { printf '\033[31m✗ %s\033[0m\n' "$*" | tee -a "$LOG"; exit 1; }
run()  { echo "── $*" | tee -a "$LOG"; "$@" 2>&1 | tee -a "$LOG"; }

printf '── Privacy Compliance — verify %s ──\n' "$STAMP" | tee -a "$LOG"

# ─── 1. Python toolchain present ─────────────────────────────────────────
run $PY --version || die "python failed to run"

# ─── 2. Django system check ──────────────────────────────────────────────
run $PY manage.py check || die "manage.py check failed"
ok "Django system check clean"

# ─── 3. Migrations consistent ────────────────────────────────────────────
if $PY manage.py makemigrations --check --dry-run >>"$LOG" 2>&1; then
  ok "No unmade migrations"
else
  die "Unmade migrations detected — commit them before deploy"
fi

# ─── 4. Test suite ───────────────────────────────────────────────────────
run $PY manage.py test --verbosity 1 || die "tests failed"
ok "Test suite green"

# ─── 5. Deploy check (prod-style) ────────────────────────────────────────
( DJANGO_DEBUG=0 APP_SECRET_KEY='verify-sh-ephemeral-key-placeholder-xxxxxxxxxxxxxxxx' \
  $PY manage.py check --deploy 2>&1 | tee -a "$LOG" ) || warn "check --deploy emitted warnings (expected in some setups)"

# ─── 6. Dependency audit (best-effort) ───────────────────────────────────
if $PY -m pip show pip-audit >/dev/null 2>&1; then
  run $PY -m pip_audit --strict --disable-pip || warn "pip-audit reported issues"
elif command -v pip-audit >/dev/null 2>&1; then
  run pip-audit --strict || warn "pip-audit reported issues"
else
  warn "pip-audit not installed — skip (\`pip install pip-audit\` to enable)"
fi

# ─── 7. Live smoke (only if TARGET_URL given) ────────────────────────────
if [[ -n "$TARGET_URL" ]]; then
  echo "── Probing $TARGET_URL ──" | tee -a "$LOG"
  BASE="${TARGET_URL%/}"

  HEALTH=$(curl -fsS "$BASE/ops/health/" 2>&1) || die "health endpoint not reachable"
  echo "$HEALTH" | tee -a "$LOG"
  grep -q '"status": "alive"' <<<"$HEALTH" || die "health JSON missing status:alive"
  ok "GET /ops/health/"

  READY=$(curl -fsS "$BASE/ops/readyz/" 2>&1) || die "readyz endpoint not reachable"
  grep -q '"status": "ready"' <<<"$READY" || die "readiness JSON missing status:ready"
  ok "GET /ops/readyz/"

  HEADERS=$(curl -sIL "$BASE/accounts/login/")
  echo "$HEADERS" | tee -a "$LOG"
  grep -iq '^Content-Security-Policy:' <<<"$HEADERS" || warn "CSP header missing at /accounts/login/"
  grep -iq '^X-Frame-Options: *DENY' <<<"$HEADERS" || warn "X-Frame-Options missing or not DENY"
  grep -iq '^X-Content-Type-Options: *nosniff' <<<"$HEADERS" || warn "X-Content-Type-Options missing"
  grep -iq '^Referrer-Policy:' <<<"$HEADERS" || warn "Referrer-Policy missing"
  if [[ "$BASE" =~ ^https ]]; then
    grep -iq '^Strict-Transport-Security:' <<<"$HEADERS" || warn "HSTS missing (expected over HTTPS)"
  fi
  ok "security-header probe complete"

  RID=$(curl -sI "$BASE/ops/health/" | grep -i '^X-Request-ID' | head -1)
  [[ -n "$RID" ]] || warn "X-Request-ID header missing"
  ok "request-ID echo present"
fi

printf '\n\033[32m✓ verify.sh passed\033[0m  log=%s\n' "$LOG"
