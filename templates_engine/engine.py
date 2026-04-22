from datetime import date

from django.template import Context, Template

from jurisdictions.models import Framework, Jurisdiction

from .models import GeneratedDocument, TemplateDefinition


def build_context(organization, jurisdiction_code: str | None = None):
    profile = getattr(organization, 'profile', None)
    jurisdiction = None
    if jurisdiction_code:
        jurisdiction = Jurisdiction.objects.filter(code=jurisdiction_code).first()
    frameworks = list(
        Framework.objects.filter(jurisdiction__code=jurisdiction_code).values_list('code', flat=True)
    ) if jurisdiction_code else list(Framework.objects.values_list('code', flat=True))

    return {
        'org': organization,
        'profile': profile,
        'jurisdiction': jurisdiction,
        'jurisdiction_code': jurisdiction_code or '',
        'frameworks': frameworks,
        'today': date.today(),
    }


def render_template(template_def: TemplateDefinition, organization, jurisdiction_code: str | None = None):
    ctx = build_context(organization, jurisdiction_code)
    tmpl = Template(template_def.body)
    return tmpl.render(Context(ctx))


def generate_document(template_def: TemplateDefinition, organization, user=None, jurisdiction_code: str | None = None, title: str | None = None):
    body = render_template(template_def, organization, jurisdiction_code)
    doc_title = title or f'{template_def.get_kind_display()} — {organization.name}'
    doc = GeneratedDocument.objects.create(
        organization=organization,
        template=template_def,
        title=doc_title,
        rendered_content=body,
        generated_by=user,
    )
    return doc
