# Privacy & Data Protection Compliance Platform — Design Spec

**Date:** 2026-04-22
**Status:** Approved for MVP build

## 1. Product Vision

**Name (working):** Sentinel — Continuous Data Protection Compliance.

**One-liner:** Tell us what your business does; we tell you exactly which data-protection laws apply across Ghana, Kenya, Nigeria, USA and Europe, track your readiness, score your risk, and generate the policies, registers and notices you need.

**Target customer:** SMEs and mid-market orgs operating in one or more of the supported jurisdictions — especially fintech, health, e-commerce, SaaS, NGOs, and any org processing personal data cross-border.

## 2. Differentiated Value (CEO view)

| Commodity behavior | Sentinel's innovation |
|---|---|
| Static compliance checklists | **Dynamic Jurisdiction Router** — scope by org profile; only relevant obligations surface |
| Generic policy templates | **Contextual Template Engine** — templates auto-fill from org profile and jurisdiction |
| Siloed country views | **Cross-jurisdictional Gap Map** — "if you're GDPR-ready, here's the delta to NDPA" |
| One-off risk scores | **Living Risk Score** — weighted by sensitivity, volume, cross-border flows, regulator activity |
| PDF audits | **Evidence Vault + Auto-ROPA** — auditable record-keeping out of the box |

**Key KPIs surfaced to the CEO/DPO:**
- Maturity Score per jurisdiction (0–100)
- Gap count (open controls) by severity
- Overdue controls
- Risk Heat Index (weighted risk rollup)
- DSAR / incident on-time %
- Regulator-readiness index (ability to produce evidence in < 72h)

## 3. Supported Jurisdictions & Frameworks (seeded in MVP)

| Jurisdiction | Framework | Authority |
|---|---|---|
| Ghana | Data Protection Act, 2012 (Act 843) | Data Protection Commission |
| Kenya | Data Protection Act, 2019 | Office of the Data Protection Commissioner (ODPC) |
| Nigeria | Nigeria Data Protection Act 2023 + NDPR | Nigeria Data Protection Commission |
| USA | CCPA / CPRA (California); placeholders for HIPAA, GLBA | California Privacy Protection Agency |
| Europe (EEA) | GDPR (Regulation 2016/679) | EDPB / national DPAs |

Each framework has: `principles`, `requirements` (atomic obligations, e.g. "Maintain ROPA"), `rights` (data subject rights), `penalties`, `notification_windows`.

## 4. System Architecture

**Stack:**
- Django 5 + Django REST Framework (for future API)
- PostgreSQL (JSONB for flexible compliance artifacts); SQLite acceptable for dev
- Server-rendered Django templates + **Tailwind CSS v4** + **HTMX** + **Alpine.js**
- Celery + Redis for async (stub in MVP, used for notifications)
- WeasyPrint for PDF template export

**Why server-rendered + HTMX:** lower JS complexity, fast iteration, meets enterprise buyer expectations for auditability. Alpine.js handles micro-interactions.

## 5. Django Apps

| App | Purpose |
|---|---|
| `accounts` | Multi-tenant orgs, users, RBAC roles, org profile |
| `jurisdictions` | Framework catalog, requirements, crosswalk, applicability engine |
| `assessments` | Scoping questionnaire, applicability results, gap analysis |
| `controls` | Control library, assignment, evidence, due dates, status |
| `risks` | Risk register, scoring engine, heatmap |
| `templates_engine` | Contextual template generator with jurisdiction variants |
| `dsar` | Data subject request intake + workflow |
| `incidents` | Breach log + regulator notification timer |
| `vendors` | Sub-processor register + DPA tracking |
| `dashboard` | KPIs, gap map, heatmap, exec reports |
| `core` | Shared utilities, base models, middleware |

## 6. Core Domain Model

```
Organization ──< OrgProfile (data categories, purposes, sectors, cross-border flows)
     │
     ├──< Assessment ──< Applicability(requirement, applicable?, rationale)
     │
     ├──< Control (framework_req, owner, status, due_date, evidence[])
     │
     ├──< Risk (title, likelihood, impact, treatment, residual_score)
     │
     ├──< GeneratedDocument (template, rendered_content, jurisdiction)
     │
     ├──< DSARRequest (subject, type, received_at, due_at, status)
     │
     └──< Incident (title, detected_at, severity, regulator_notified)

Framework ──< Requirement ──< Crosswalk(mapped_requirement_in_other_framework)
```

Key fields on `OrgProfile`:
- `sectors[]` (fintech, health, e-commerce, saas, education, ngo, public)
- `data_categories[]` (PII, special-category, children, financial, health, biometric, location)
- `processing_purposes[]`
- `data_subject_locations[]` (country codes)
- `cross_border_transfers` (bool), `transfer_mechanisms[]`
- `annual_revenue_band`, `employee_count_band`
- `has_eu_establishment` / `processes_eu_residents`
- `offers_to_california_residents`
- `uses_automated_decision_making`

## 7. Applicability Engine

`jurisdictions/applicability.py` — rule-based DSL. Each requirement has an `applicability_rule` expressed as a small Python callable operating on `OrgProfile`. Examples:

- GDPR applies if `has_eu_establishment OR processes_eu_residents`
- Ghana DPA applies if `data_subject_locations contains 'GH' OR has_gh_establishment`
- NDPA applies if `data_subject_locations contains 'NG' OR has_ng_establishment`
- CCPA applies if `offers_to_california_residents AND (revenue > $25M OR handles 100k+ consumers OR >50% revenue from selling data)`

Per requirement we return `{applicable: bool, rationale: str, obligations: [...]}`.

## 8. Crosswalk

`jurisdictions/crosswalk.py` — many-to-many `RequirementMapping(source_req, target_req, equivalence)` with values `equivalent | stricter | weaker | partial`. UI exposes "If you've done X under GDPR, here's what's still needed for NDPA".

## 9. Risk Scoring

`risks/scoring.py`:

```
inherent = likelihood (1–5) × impact (1–5)
data_sensitivity_modifier = f(data_categories)  # e.g. health = +2, special = +2
volume_modifier = log-scale(data_volume)
jurisdiction_activity_modifier = regulator_activity_index[jurisdiction]
residual = inherent × control_effectiveness_factor (0.2–1.0)
heat_score = residual × modifiers
```

Heatmap uses residual × likelihood / impact grid.

## 10. Template Engine

`templates_engine/engine.py` — Jinja-style substitution of `{{ org.name }}`, `{{ jurisdiction.authority }}`, etc., with conditional blocks per jurisdiction:

```
{% if 'GDPR' in frameworks %}
  Under Article 15 of GDPR you have the right to access...
{% endif %}
{% if 'NDPA' in frameworks %}
  Under Section 34 of the NDPA 2023 you have the right to...
{% endif %}
```

**MVP templates (5 jurisdictions each):**
1. Privacy Notice / Privacy Policy
2. Record of Processing Activities (ROPA / Art. 30)
3. Data Subject Access Request (DSAR) response

Export as Markdown + HTML; PDF via WeasyPrint.

## 11. UI/UX

**Design language:** clean, trustworthy, enterprise-serious. Color system: deep indigo primary, emerald for "compliant", amber/orange for "partial", rose/red for "gap", slate neutrals. Rounded-lg corners, subtle shadows, focus rings for accessibility.

**Key screens:**
1. **Onboarding Wizard** (3 steps): org basics → data profile → jurisdictions in scope → result: applicable frameworks + initial checklist
2. **Compliance Command Center** (dashboard): maturity tiles per jurisdiction, KPI strip, top risks, overdue controls, 90-day trend
3. **Gap Map**: jurisdictions × requirement categories grid, colored by coverage
4. **Requirements / Controls**: filterable list, kanban-style statuses, evidence upload
5. **Risk Register**: table + heatmap
6. **Templates**: browse → generate → preview → download
7. **DSAR & Incidents**: intake + timelines

**Accessibility:** semantic HTML, ARIA labels, keyboard navigable, WCAG 2.2 AA color contrast, focus-visible rings.

## 12. MVP Scope (this build)

**In:**
- Django project scaffolded with all 11 apps
- Seeded jurisdictions & sample requirements for GDPR, Ghana DPA, Kenya DPA, NDPA, CCPA
- Applicability engine
- Crosswalk (sample mappings)
- Controls + progress tracking
- Risk register + scoring + heatmap
- Template engine + 3 × 5 = 15 templates (stubs for jurisdictions)
- Dashboard with KPIs + gap map
- Onboarding wizard
- Auth (Django built-in) + basic RBAC
- Tests for applicability, risk scoring, template rendering
- Seed management command

**Deferred (documented for v2):**
- Vendor / sub-processor register full workflow
- Incident timer + regulator notification auto-draft
- DSAR portal for subjects
- SSO, Billing
- Full i18n / French, Swahili localization
- Webhooks / API keys for integrations
- Mobile responsive pass beyond core screens

## 13. Testing Strategy

- Unit tests: applicability engine, crosswalk, risk scoring, template rendering
- View tests: smoke tests for each core page returns 200 logged-in
- Seed integrity test: loading fixtures produces expected counts
- Manual QA via the `investigate` and `qa` skills in `skills/` at the end

## 14. Acceptance Criteria

1. A new user can sign up, complete the wizard, and land on a populated dashboard within 2 minutes.
2. For a sample org profile (e.g., Ghanaian fintech also serving EU), the applicability engine returns Ghana DPA + GDPR as applicable, CCPA as not applicable, with rationales.
3. The gap map shows all 5 jurisdictions with at least 1 requirement each.
4. A user can generate a Privacy Notice for any applicable jurisdiction and download HTML.
5. Risk register accepts a risk and computes a residual score.
6. All tests pass.

## 15. Out-of-scope Risks Accepted

- Legal accuracy is best-effort for MVP; the platform includes a "this is not legal advice" disclaimer. Real production deployment would require a jurisdiction counsel review pass.
- Regulator-specific forms (e.g., ODPC registration forms) are not auto-submitted.
