"""Form helpers.

``scope_form_to_org`` narrows every ModelChoiceField / ModelMultipleChoiceField
on a form to rows belonging to the active organisation, preventing cross-tenant
data leakage through HTML ``<select>`` options.
"""
from django.forms import ModelChoiceField, ModelMultipleChoiceField

from accounts.models import Membership


GLOBAL_CATALOG_LABELS = {
    # Shared reference data — never scoped per-tenant.
    'jurisdictions.Jurisdiction',
    'jurisdictions.Framework',
    'jurisdictions.Requirement',
    'templates_engine.TemplateDefinition',
}


def scope_form_to_org(form, org):
    """Narrow every FK / M2M on ``form`` to ``org``-visible rows.

    * User-typed fields are narrowed to users who have a Membership in org.
    * Models with an ``organization`` FK are filtered by that FK.
    * Global catalogues (jurisdictions, templates) are left untouched.
    """
    if org is None:
        return form

    user_ids = None
    for field in form.fields.values():
        if not isinstance(field, (ModelChoiceField, ModelMultipleChoiceField)):
            continue
        model = field.queryset.model
        label = model._meta.label

        if label in GLOBAL_CATALOG_LABELS:
            continue

        if label == 'accounts.User':
            if user_ids is None:
                user_ids = list(
                    Membership.objects.filter(organization=org)
                    .values_list('user_id', flat=True)
                )
            field.queryset = field.queryset.filter(pk__in=user_ids)
            continue

        if any(f.name == 'organization' for f in model._meta.get_fields()):
            field.queryset = field.queryset.filter(organization=org)

    return form
