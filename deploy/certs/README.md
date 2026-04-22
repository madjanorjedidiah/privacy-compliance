# TLS certs for the standalone deployment

The standalone `docker-compose.yml` mounts this directory into `nginx` as
`/etc/nginx/certs`. Nginx expects two files:

- `fullchain.pem` — server cert + intermediates
- `privkey.pem` — private key

## How they get there

- **Self-signed (dev / first boot):** run `../../scripts/init-standalone.sh`
  (or the one-shot `../../scripts/quickstart.sh`). Generates a 398-day
  self-signed cert for `CN=localhost` (override with an argument).
- **Let's Encrypt (prod):** start the `certbot` sidecar with the
  `letsencrypt` compose profile — see README.md "Let's Encrypt" section.

The real `.pem` files are gitignored. This `.keep` keeps the directory
in version control so the compose volume mount doesn't fail on first clone.
