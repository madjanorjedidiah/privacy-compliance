# Contributing

Thanks for considering a contribution. This is a free, community-maintained
data-protection compliance platform — self-hosted by any organisation that
needs it, anywhere in Ghana, Kenya, Nigeria, the EU, or the USA.

> **New here?** Read [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) and
> [`SECURITY.md`](SECURITY.md) first.

## Ways to contribute

| Type | What we'd love | What we won't accept |
|---|---|---|
| **Bug reports** | Reproducible steps, expected vs actual, versions | "It's broken" with no context |
| **Bug fixes** | PRs with a failing test → passing test | Fixes without tests |
| **Feature PRs** | Open a Discussion or Issue **first** so we agree on scope | Large unsolicited rewrites |
| **Jurisdiction content** | New frameworks + requirements + crosswalk entries, with source citations | Unsourced legal content |
| **Template content** | Jurisdiction-aware policy templates with DPO review | Templates copied from proprietary sources |
| **Docs** | Clearer README, better deploy guides, translations | AI-generated slop with no factual anchor |
| **Compliance reviews** | DPOs + lawyers opening Issues flagging gaps in `COMPLIANCE.md` | Drive-by legal opinions |

## Local setup

```bash
python3.13 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_jurisdictions
.venv/bin/python manage.py seed_templates
.venv/bin/python manage.py seed_demo        # demo workspace at 0% compliance
.venv/bin/python manage.py runserver
```

Open http://127.0.0.1:8000 and log in as `demo` / `demodemo123!`.

## Running the checks

Before you push:

```bash
./scripts/verify.sh
```

That runs system check, migration-consistency check, the full test suite,
and (optionally) `pip-audit`. PRs that don't pass `verify.sh` won't be merged.

## Pull request checklist

- [ ] Branch name describes the change, e.g. `fix/ropa-form-owner-leak`
- [ ] New or modified behaviour has a test
- [ ] `./scripts/verify.sh` exits 0
- [ ] No migrations merged without review — new models need schema discussion
- [ ] Any new dependency is justified in the PR body (size + maintenance)
- [ ] Commit messages describe *why*, not just *what* — your future self will thank you
- [ ] Docs / `COMPLIANCE.md` / template content updated if behaviour changes

## Code style

- Python 3.13+, Django 5.1.
- `ruff` / `black` style where practical — readability over cleverness.
- Views that mutate state are decorated with `@write_required` from
  `accounts.permissions`.
- Multi-tenant queries always start with `filter(organization=request.active_org)`
  or use `get_object_or_404(..., organization=org)`.
- Forms with FK fields must call `scope_form_to_org(form, org)` from
  `core.forms` — tenant isolation is our #1 invariant.

## Licensing

This project is licensed under the **GNU Affero General Public License v3.0
or later** (AGPL-3.0-or-later) — see [`LICENSE`](LICENSE).

By submitting a patch, you agree your contribution is licensed under the same
terms. **Do not submit code that you do not have the right to license under
AGPL-3.0.**

The AGPL ensures the platform stays free: anyone who runs a modified version
as a network service must share their source with users of that service.
This matches the project's mission of making compliance tooling a public
good, not a lock-in.

## Governance

- Maintainers merge via PR after one review + green CI.
- Large or legally-sensitive changes (jurisdiction content, cryptography,
  RBAC) require two reviews — at least one from a maintainer with a DPO
  qualification.
- Controversial architectural changes go through a short design note (one
  markdown file in `docs/superpowers/specs/`).
- Release cadence is at maintainer discretion — no commercial deadline
  pressure.

## Security disclosures

**Do not file security issues on the public tracker.** See
[`SECURITY.md`](SECURITY.md).

## Questions?

Open a GitHub Discussion. If you're not sure whether something is a bug,
a feature request, or a question — it's probably a Discussion.
