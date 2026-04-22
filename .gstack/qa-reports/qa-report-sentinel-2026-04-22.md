# QA Report — Sentinel (Privacy & Data Protection Compliance Platform)

**Date:** 2026-04-22
**Build:** MVP walking-skeleton
**Environment:** Dev server on 127.0.0.1:8088, SQLite, Django 5.1.15, Python 3.13
**Tester:** Automated curl-driven QA pass

## Health Score: **92 / 100** (Green)

## Coverage
- 17 authenticated URL paths probed — all HTTP 200
- Full signup → 3-step onboarding → dashboard round-trip validated as a new user
- Template generation + download round-trip validated (Ghana Privacy Notice)
- HTMX quick-status control-update validated
- Django unit tests: **27/27 pass** across 5 apps (applicability, risk scoring, templates, assessment flow, dashboard services + views)

## Issues Found

### [FIXED] Risk heatmap Y-axis labels all rendered as "I1"
- **Severity:** Low (cosmetic)
- **Where:** `templates/risks/list.html:44`
- **Root cause:** Used `{{ 5|add:"-"|add:forloop.counter|add:"1" }}` which Django's `add` filter cannot chain as arithmetic.
- **Fix:** Compute impact labels in `risks/views.py:risks_list` and pass pre-built `heatmap_rows` to the template.
- **Verification:** Heatmap now renders I5, I4, I3, I2, I1 top-to-bottom (confirmed via HTML inspection of `/risks/`).

## Observations (not bugs)

1. **Deploy-check warnings** (`security.W004/W008/W009/W012/W016/W018`) are expected in DEBUG mode. Before production: set `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, a strong `SECRET_KEY`, and `DEBUG=False`. Pre-wired via environment variables in `sentinel/settings.py`.
2. **Static files** — Tailwind ships via CDN for MVP. For production, switch to a compiled Tailwind build (`@tailwindcss/cli` + JIT) to shrink payload and allow CSP tightening.
3. **Legal disclaimer** — Displayed on every page footer per spec §15. Regulator-registration forms are not auto-submitted (out-of-scope for MVP).
4. **Accessibility** — Form labels present, focus-ring styles defined. Full WCAG 2.2 AA sweep deferred to v2.

## Feature Readiness Matrix

| Capability | Status | Evidence |
|---|---|---|
| Multi-tenant signup + auth | ✅ | signup → onboarding smoke test, `Membership` records |
| Applicability engine (5 jurisdictions) | ✅ | 9 tests pass; demo org yields correct GH+EU+CCPA+KE+NG applicability |
| Crosswalk (cross-jurisdiction) | ✅ | 13 mappings seeded; rendered on requirement pages |
| Controls + progress tracking | ✅ | 40 controls auto-provisioned for Kudu Fintech |
| HTMX inline status update | ✅ | returns swapped `<tr>`, no full reload |
| Risk register + scoring | ✅ | 3 scoring tests pass; heatmap renders; severity labels wired |
| Template engine + 7 templates | ✅ | Ghana Privacy Notice generated with correct org context; download = 37 lines markdown |
| DSAR intake + timers | ✅ | 30-day SLA computed; overdue flag; list/detail views render |
| Incident register + 72h deadline | ✅ | auto-deadline; mark-notified / resolve actions wired |
| Jurisdiction catalog | ✅ | 5 jurisdictions × frameworks × requirements browsable |
| Executive dashboard | ✅ | KPI snapshot, maturity-per-framework, top risks, overdue list |
| Gap Map | ✅ | jurisdictions × 14 requirement categories grid with color-coded coverage |
| Admin | ✅ | Registered for User, Organization, Profile, Membership, Jurisdiction, Framework, Requirement, RequirementMapping |

## Deferred / Follow-on

- Vendor register workflow (model exists, UI deferred)
- Full DSAR subject-facing portal
- SSO, Billing, API keys
- i18n (French, Swahili)
- Compiled Tailwind pipeline
- PDF export (library chosen: WeasyPrint; implementation deferred)
- Automated regulator-notification email drafts

## Verdict

**Ready for v0 demo.** All acceptance criteria from the design spec (§14) pass:
1. ✅ Signup → populated dashboard in under 2 minutes
2. ✅ Ghanaian fintech profile yields GH DPA + GDPR + CCPA + NDPA + KE applicability with rationales
3. ✅ Gap map shows all 5 jurisdictions
4. ✅ Privacy Notice generated + downloaded
5. ✅ Risk register accepts risks + computes residual scores
6. ✅ All tests pass (27/27)
