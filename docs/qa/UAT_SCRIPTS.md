# UAT Scripts — by role

One walk-through per `Membership.Role`. Each script is a copy-paste
checklist a human can execute against a freshly-seeded workspace. Tick
the box when the step passes; record any anomaly in the "Notes" column.

All scripts assume the app is running at `http://127.0.0.1:8000/` (local)
or at your deploy URL.

---

## Common setup — one-time, pre-script

1. Fresh workspace:
   ```
   .venv/bin/python manage.py seed_demo       # re-provisions Kudu Fintech at 0%
   ```
2. Create one extra user per role you're testing:
   ```python
   # .venv/bin/python manage.py shell -c "
   from accounts.models import Membership, Organization
   from django.contrib.auth import get_user_model
   U = get_user_model()
   org = Organization.objects.get(slug='kudu-fintech')
   for uname, role in [('uat_dpo','dpo'), ('uat_comp','compliance'), ('uat_audit','auditor'), ('uat_view','viewer')]:
       u, _ = U.objects.get_or_create(username=uname, defaults={'email': uname+'@example.test'})
       u.set_password('UatPass-2026!')
       u.save()
       Membership.objects.get_or_create(user=u, organization=org, defaults={'role': role, 'is_primary': True})
   "
   ```

---

## Script A — Owner (`demo / demodemo123!`)

Owner is the all-rights role. Every button should work.

| # | Step | Expected | ✓ | Notes |
|---|---|---|---|---|
| A1 | Log in | Redirected to `/dashboard/` | | |
| A2 | See Compliance score 0/100 red | Score ring is rose, "0 of 40 policies implemented" hint | | |
| A3 | Click the score tile | Lands on `/compliance/` with 5 jurisdiction cards | | |
| A4 | Click Ghana jurisdiction card | Requirements listed grouped by category | | |
| A5 | On `GH-Registration`, click "Implemented" | Pill turns emerald, score rises, flash message shows new status | | |
| A6 | Click "Use template" on a Privacy Notice row | Pre-filled document opens; Kudu Fintech + "Data Protection Commission" + "Act 843" appear | | |
| A7 | Download the template as .md | File downloads with a correct filename | | |
| A8 | Navigate to ROPA → "Add processing activity" | Form loads; `owner` dropdown shows only demo + UAT users | | |
| A9 | Save one complete activity | Detail page renders with all values | | |
| A10 | Go to Vendors → Add vendor | Form saves; DPA expiry within 60 days paints the row amber on list | | |
| A11 | Go to DPIAs → Register a DPIA with 3 triggers ticked | `DPIA required` badge appears on detail page | | |
| A12 | Go to Retention → Add a policy with legal_hold=True | Row flagged "Legal hold" in list | | |
| A13 | Go to Training → Add module, then Record a completion | Expires_on auto-populated from module refresh_months | | |
| A14 | Go to Risks → Add a risk with L4×I4, sensitivity 5 | Severity pill is CRITICAL | | |
| A15 | Go to DSAR → Log a request for a `US-CA` subject | Due date = received + 45 days | | |
| A16 | Go to Incidents → Log an incident with `affected_jurisdictions=['EU']` | 72-hour deadline present | | |
| A17 | Go to Profile | "Download my data" and "Delete my account" visible | | |
| A18 | Click Download my data | JSON downloads with username, memberships, auth_events | | |
| A19 | Attempt to Delete account | Blocked — sole owner message | | |
| A20 | Sign out | Redirected to `/accounts/login/`; `AuthEvent` LOGOUT row created (check via `/admin/accounts/authevent/`) | | |

---

## Script B — DPO (`uat_dpo / UatPass-2026!`)

DPO should have full write access across DPO registers.

| # | Step | Expected | ✓ | Notes |
|---|---|---|---|---|
| B1 | Log in | Dashboard loads | | |
| B2 | Create a DPIA | Success | | |
| B3 | Assign yourself as DPO on the DPIA | Form saves | | |
| B4 | Update a processing activity's `lawful_basis` | Success | | |
| B5 | Export your account data | JSON bundle returned | | |
| B6 | Verify no access to `/admin/` | Redirects to admin login | | |

---

## Script C — Compliance Officer (`uat_comp / UatPass-2026!`)

Compliance Officer is a write-enabled operational role.

| # | Step | Expected | ✓ | Notes |
|---|---|---|---|---|
| C1 | Log in | Dashboard loads | | |
| C2 | Advance 5 controls from Not-started → Implemented | Score moves; 5 `ControlStatusChange` rows written | | |
| C3 | Upload an evidence file (2 MB PDF) | Upload succeeds, file linked in evidence list | | |
| C4 | Upload an evidence file (20 MB arbitrary binary) | Rejected with file-size validation error | | |
| C5 | Try to upload a `.exe` | Rejected with file-extension validation error | | |
| C6 | Close a DSAR request | Request moves to `Closed`; closed_at stamped | | |

---

## Script D — Auditor (`uat_audit / UatPass-2026!`)

Auditor is read-only. Every write should fail.

| # | Step | Expected | ✓ | Notes |
|---|---|---|---|---|
| D1 | Log in | Dashboard loads | | |
| D2 | Navigate to Compliance Checks → Ghana | Page renders | | |
| D3 | Click `Implemented` on a control | **403 Forbidden** | | |
| D4 | Navigate to ROPA | List renders (read-only OK) | | |
| D5 | Click "Add processing activity" | **403 Forbidden** | | |
| D6 | Navigate to `/templates/` | List renders | | |
| D7 | Click "Generate" on any template | **403 Forbidden** | | |
| D8 | Try `POST /accounts/me/delete/` with confirm | Blocked (read-only role or sole-owner) | | |

---

## Script E — Viewer (`uat_view / UatPass-2026!`)

Viewer sees Dashboard + Compliance, no edit at all.

| # | Step | Expected | ✓ | Notes |
|---|---|---|---|---|
| E1 | Log in | Dashboard loads | | |
| E2 | See Compliance Checks → Ghana | Renders | | |
| E3 | Click a control's `Implemented` | **403 Forbidden** | | |
| E4 | Navigate to Risks | Renders | | |
| E5 | Click Edit on any risk | **403 Forbidden** | | |

---

## Cross-cutting tenant-isolation probe (2 browsers)

1. Owner A in tenant 1, Owner B in tenant 2.
2. B copies the URL of one of their own processing activities, e.g. `/ropa/42/`.
3. A pastes that URL into their address bar while logged in.
4. **Expected:** 404. Repeat for every module (controls, risks, DSARs, incidents, DPIAs, retention, vendors, training).

---

## Sign-off

| Role | Tester | Date | Pass? |
|---|---|---|---|
| Owner |  |  |  |
| DPO |  |  |  |
| Compliance |  |  |  |
| Auditor |  |  |  |
| Viewer |  |  |  |
| Tenant-isolation probe |  |  |  |
