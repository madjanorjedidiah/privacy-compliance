from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .engine import generate_document, render_template
from .models import GeneratedDocument, TemplateDefinition


@login_required
def templates_list(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    templates = TemplateDefinition.objects.all()
    documents = GeneratedDocument.objects.filter(organization=org)
    return render(request, 'templates_engine/list.html', {
        'templates': templates, 'documents': documents,
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


@login_required
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
