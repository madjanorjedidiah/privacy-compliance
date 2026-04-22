from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import write_required

from .engine import generate_document, render_template
from .models import GeneratedDocument, TemplateDefinition


@login_required
def templates_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')

    from jurisdictions.models import Jurisdiction
    jurisdictions = list(Jurisdiction.objects.prefetch_related('frameworks').all())

    templates = (
        TemplateDefinition.objects
        .prefetch_related('requirements__framework__jurisdiction')
    )

    buckets = {j.code: {'jurisdiction': j, 'templates': []} for j in jurisdictions}
    universal = []
    for t in templates:
        juris_codes = set()
        if t.jurisdiction_code:
            juris_codes.add(t.jurisdiction_code)
        for req in t.requirements.all():
            juris_codes.add(req.framework.jurisdiction.code)
        if juris_codes:
            for code in juris_codes:
                if code in buckets:
                    buckets[code]['templates'].append(t)
        else:
            universal.append(t)

    jurisdiction_cards = [
        v for v in buckets.values() if v['templates']
    ] + ([{'jurisdiction': None, 'templates': universal, 'is_universal': True}] if universal else [])

    documents = GeneratedDocument.objects.filter(organization=org)
    return render(request, 'templates_engine/list.html', {
        'jurisdiction_cards': jurisdiction_cards,
        'documents': documents,
    })


@login_required
def template_preview(request, pk):
    org = request.active_org
    tmpl = get_object_or_404(TemplateDefinition, pk=pk)
    jurisdiction_code = request.GET.get('jurisdiction', tmpl.jurisdiction_code)
    body = render_template(tmpl, org, jurisdiction_code or None)
    return render(request, 'templates_engine/preview.html', {
        'template': tmpl, 'body': body, 'jurisdiction_code': jurisdiction_code,
    })


@write_required
def template_generate(request, pk):
    org = request.active_org
    tmpl = get_object_or_404(TemplateDefinition, pk=pk)
    jurisdiction_code = request.POST.get('jurisdiction', tmpl.jurisdiction_code) or None
    doc = generate_document(tmpl, org, user=request.user, jurisdiction_code=jurisdiction_code)
    messages.success(request, f'Document generated: {doc.title}')
    return redirect('templates:document', pk=doc.pk)


@login_required
def document_detail(request, pk):
    org = request.active_org
    doc = get_object_or_404(GeneratedDocument, pk=pk, organization=org)
    return render(request, 'templates_engine/document.html', {'doc': doc})


@login_required
def document_download(request, pk):
    org = request.active_org
    doc = get_object_or_404(GeneratedDocument, pk=pk, organization=org)
    filename = f'{doc.template.kind}-{org.slug}.md'
    response = HttpResponse(doc.rendered_content, content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
