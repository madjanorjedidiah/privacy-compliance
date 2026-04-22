# Compliance Mapping

How the **platform itself** (as opposed to the compliance workflows it runs
for customers) meets the obligations of GDPR, Ghana DPA 2012 (Act 843),
Kenya DPA 2019, Nigeria NDPA 2023, CCPA/CPRA, and ISO/IEC 27001 + 27701.

> This document is an internal control map, not a warranty. It should be
> reviewed with counsel before go-live and annually thereafter.

---

## 1. GDPR / Kenya DPA / NDPA — core obligations

| Obligation | Article / Section | How the platform meets it |
|---|---|---|
| Lawful basis for processing app-user data | GDPR Art. 6; KE DPA §30; NDPA §25 | `/privacy/` notice declares contract + legitimate interests. No Art. 9 data of app users. |
| Transparency / privacy notice | GDPR Arts. 12-14; Ghana DPA §24; KE §29; NDPA §27 | Public page at [`/privacy/`](templates/public/privacy_notice.html). |
| Data subject rights | GDPR Arts. 15-22; Ghana §§32-37; KE §26 | Self-service export (Art. 15) + erasure (Art. 17) at [`/accounts/profile/`](accounts/data_subject_views.py). Other rights via email. |
| Record of processing activities | GDPR Art. 30; NDPA §29 | `ropa` app — structured controller/processor ROPA per tenant. |
| Privacy by design | GDPR Art. 25 | Per-tenant query scoping (middleware + form filtering), least-privilege RBAC, evidence file validation, encryption in transit. |
| Security of processing | GDPR Art. 32; Ghana §28; KE §41; NDPA §39 | HSTS 1y, TLS enforced via NPM, secure cookies, password min 10 + common-pw check, django-axes lockout (5 attempts / 1h), CSP headers, rate limits on auth, JSONField input validators. |
| DPIA | GDPR Art. 35; KE §31 | `dpia` app — EDPB 9-trigger screen, inherent + residual scoring, formal sign-off. |
| Breach notification | GDPR Art. 33 (72h); KE §43; NDPA §40 | `incidents` app stamps a 72-hour regulator deadline on detection; per-jurisdiction overrides in settings. |
| International transfers | GDPR Chap. V; Ghana §47; KE §§48-50; NDPA §§41-43 | `vendors` captures transfer mechanism + TIA flag; ROPA tracks destination countries. |
| DPO designation | GDPR Art. 37; NDPA §32 | `Membership.Role.DPO` + owner contact surfaced in onboarding. |
| Breach + auth trail | GDPR Art. 5(2) accountability | `controls.ControlStatusChange` + `accounts.AuthEvent` (append-only). |

## 2. CCPA / CPRA (California)

| Obligation | Section | How met |
|---|---|---|
| Notice at collection | §1798.100 | `/privacy/` covers categories, purposes, retention. |
| Right to know / delete / correct | §§1798.105-.125 | Self-service export + delete (45-day SLA honoured via per-jurisdiction deadline map). |
| Do Not Sell / Share | §1798.135 | Platform does not sell or share personal information. Documented in `/privacy/` §4. |
| Sensitive personal information | §1798.121 | Not processed for app users. |
| Service-provider contracts | §1798.100(d) | Sub-processor DPA list maintained; exposed in `vendors` register. |

## 3. Ghana Data Protection Act 2012 — operator obligations

| Obligation | Section | How met / operator action required |
|---|---|---|
| Registration as data controller | §§27-29 | **Operator action**: register the company that runs the deployed platform with the Ghana DPC before go-live. Renew annually. See `GO_LIVE.md`. |
| Apply the 8 principles | §17 | Written policy (this doc); technical controls enforce minimisation and retention. |
| Obtain consent or lawful ground | §20 | Documented in `/privacy/`. |
| Notice at collection | §24 | `/privacy/` page. |
| Security measures | §28 | See GDPR Art. 32 row. |
| Data subject rights | §§32-37 | Self-service tools + email channel. |
| Lawful transfers | §47 | TIA flag on `Vendor` records; documented in `/privacy/` §6. |

## 4. ISO/IEC 27001 (InfoSec) + 27701 (Privacy)

| Control family | Relevant 27001/27701 clause | Platform control |
|---|---|---|
| A.5 — Policies | 5.1.1 | This doc + `/privacy/` + `/terms/`. |
| A.5 — Access control | 5.15–5.18 | Django auth, `accounts.permissions.write_required`, role-gated views, tenant scoping. |
| A.5 — Identity | 5.16 | `accounts.Membership` roles; partial unique `is_primary` constraint. |
| A.5 — Cryptography | 8.24 | TLS via NPM + HSTS 1y; `fernet`/app-level crypto available for future evidence encryption. |
| A.5 — Physical | 7.x | Hosted on shared infra; controls inherited from hosting provider (document in DPA). |
| A.5 — Ops security | 8.15 logging | `AuthEvent`, `ControlStatusChange`, structured JSON logs with request IDs. |
| A.5 — Comms security | 8.20 | HSTS, CSP, SecureProxySSLHeader, same-origin referrer. |
| A.5 — System acq / dev | 8.25-27 | Form validators, file-extension whitelist + size cap, CSP. |
| A.5 — Supplier rel. | 5.19-23 | `vendors` app tracks DPAs + TIAs + audit cadence. |
| A.5 — Incident mgmt | 5.24-28 | `incidents` app + 72h deadline timer + regulator notification letter template. |
| A.5 — BC / disaster | 5.29-30 | Stateless web tier + Postgres backups (operator owns). |
| A.5 — Compliance | 5.31-34 | This mapping; ROPA app; DPIA register; crosswalk engine. |
| 27701 — PIMS controls | 7.2.1-7.2.8 | Lawful basis, purpose, retention, rights, transfers all modelled in the domain. |

## 5. OWASP ASVS v4 — quick checklist

| Requirement | Status |
|---|---|
| V2 Authentication — strong password hashing | ✅ Django default (PBKDF2) + min length 10 |
| V3 Session — secure cookies, rotation on login | ✅ prod mode |
| V4 Access control — tenant isolation | ✅ middleware + `get_object_or_404(org=...)` + form scoping (63 tests) |
| V5 Validation — input trust boundary | ✅ JSONField validators, `FileExtensionValidator`, rate limits |
| V7 Error handling — no stack traces in prod | ✅ `DEBUG=0` |
| V9 Communications — TLS | ✅ NPM + HSTS 1y |
| V10 Malicious code — CSP | ✅ `django-csp` |
| V11 Business logic — rate limits | ✅ per-IP behind proxy (X-Forwarded-For) |
| V12 Files — validated uploads, size cap | ✅ extension whitelist + 10 MiB |

## 6. Residual risks / known gaps

- Evidence file anti-virus scan — not yet wired (recommend ClamAV on `/media/`).
- Single-tenant Postgres schema; for strict physical isolation deploy one DB per tenant.
- WebAuthn / MFA — not yet implemented (roadmap item).
- Field-level encryption of sensitive DSAR free-text — not yet implemented.

These are tracked as open follow-ups, not blockers for a first production
go-live with a single customer, subject to a compensating DPA.
