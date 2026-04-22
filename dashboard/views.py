from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from assessments.models import FrameworkApplicability
from assessments.services import latest_assessment

from .services import (
    gap_map,
    kpi_snapshot,
    maturity_per_framework,
    overdue_controls,
    top_risks,
)


@login_required
def home(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    if not org.onboarded_at:
        return redirect('onboarding:basics')

    kpis = kpi_snapshot(org)
    maturity = maturity_per_framework(org)
    assessment = latest_assessment(org)
    applicable_frameworks = (
        FrameworkApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .select_related('framework__jurisdiction')
        if assessment else []
    )
    not_applicable_frameworks = (
        FrameworkApplicability.objects
        .filter(assessment=assessment, applicable=False)
        .select_related('framework__jurisdiction')
        if assessment else []
    )

    return render(request, 'dashboard/home.html', {
        'kpis': kpis,
        'maturity': maturity,
        'assessment': assessment,
        'applicable_frameworks': applicable_frameworks,
        'not_applicable_frameworks': not_applicable_frameworks,
        'top_risks': top_risks(org),
        'overdue_controls': overdue_controls(org),
    })


@login_required
def gap_map_view(request):
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    data = gap_map(org)
    return render(request, 'dashboard/gap_map.html', data)
