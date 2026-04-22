from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Framework, Jurisdiction, Requirement


@login_required
def jurisdictions_list(request):
    jurisdictions = Jurisdiction.objects.prefetch_related('frameworks').all()
    return render(request, 'jurisdictions/list.html', {'jurisdictions': jurisdictions})


@login_required
def framework_detail(request, code):
    framework = get_object_or_404(Framework.objects.select_related('jurisdiction'), code=code)
    requirements = framework.requirements.all()
    return render(request, 'jurisdictions/framework.html', {
        'framework': framework, 'requirements': requirements,
    })


@login_required
def requirement_detail(request, pk):
    req = get_object_or_404(
        Requirement.objects.select_related('framework__jurisdiction'), pk=pk
    )
    mappings = req.mappings_out.select_related('target__framework__jurisdiction').all()
    reverse_mappings = req.mappings_in.select_related('source__framework__jurisdiction').all()
    return render(request, 'jurisdictions/requirement.html', {
        'req': req, 'mappings': mappings, 'reverse_mappings': reverse_mappings,
    })
