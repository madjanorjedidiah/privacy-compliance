# Security Policy

## Supported versions

This is a rolling-release project. Security fixes land on the `main` branch
and are pushed to the deploy pipeline immediately. Operators should track
`main` and pull regularly.

If you are running a fork or a pinned commit and cannot upgrade, document
the backport yourself — we do not maintain support branches.

## Reporting a vulnerability

**Please do not open a public GitHub Issue for a suspected vulnerability.**

Email **privacy@cocoatool.org** with:

- A short description of the vulnerability
- Affected commit SHA or release tag
- Steps to reproduce (a minimal PoC is ideal)
- Your assessment of impact (confidentiality / integrity / availability)
- Any suggested mitigation

We aim to:

| Step | Target time |
|---|---|
| Acknowledge receipt | 48 hours |
| Triage + initial assessment | 7 days |
| Patch published for Critical/High | 30 days |
| Patch published for Medium | 60 days |
| Credit + public advisory | After a coordinated fix ships |

If you don't receive an acknowledgement in 48 hours, escalate by emailing
the same address with `[ESCALATION]` in the subject.

## In scope

- The code in this repository
- Official Docker images published from this repo
- Documentation that could mislead a deploying organisation into an
  insecure configuration

## Out of scope

- Third-party deployments — please report to the operator of that
  deployment directly
- Reports from automated scanners without human verification
- Social engineering against project maintainers
- Denial-of-service via brute force (our rate limiter + `django-axes`
  config is the hardening; if you find a way around it, that's in scope)

## Coordinated disclosure

If you need more time than the targets above for patch distribution (e.g.
the vulnerability affects many deployed instances and public disclosure
would leave operators exposed before they patch), tell us in the initial
report and we will discuss a longer embargo.

## Hall of fame

Researchers who report responsibly and allow a fix to ship before
disclosure are credited in the release notes and can be listed here by
request. We cannot offer monetary bounties — the project is free software
with no budget.
