"""
Compliance Checks — jurisdiction-grouped view of applicable requirements
with one-click status advance and direct-to-template handoff.
"""
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from assessments.models import RequirementApplicability
from assessments.services import latest_assessment
from core.choices import ControlStatus
from dashboard.services import (
    jurisdiction_scorecard,
    weighted_maturity,
)
from jurisdictions.models import Jurisdiction, RequirementCategory

from .models import Control


STATUS_ORDER = [
    ControlStatus.NOT_STARTED,
    ControlStatus.IN_PROGRESS,
    ControlStatus.IMPLEMENTED,
]


@login_required
def compliance_home(request):
    """Landing page — scorecard per jurisdiction, link into each."""
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    if not org.onboarded_at:
        return redirect('onboarding:basics')

    scorecards = jurisdiction_scorecard(org)
    overall = weighted_maturity(org)
    return render(request, 'compliance/home.html', {
        'scorecards': scorecards,
        'overall_score': overall['score'],
        'overall_total': overall['total_requirements'],
        'overall_done': overall['done_requirements'],
    })


@login_required
def compliance_jurisdiction(request, code):
    """Per-jurisdiction list of applicable requirements grouped by category."""
    org = request.active_org
    if not org:
        return redirect('accounts:signup')
    jurisdiction = get_object_or_404(Jurisdiction, code=code)

    assessment = latest_assessment(org)
    if not assessment:
        return redirect('onboarding:basics')

    applicable = (
        RequirementApplicability.objects
        .filter(
            assessment=assessment,
            applicable=True,
            requirement__framework__jurisdiction=jurisdiction,
        )
        .select_related('requirement__framework')
        .order_by('requirement__category', 'requirement__code')
    )

    controls = {
        c.requirement_id: c
        for c in Control.objects.filter(
            organization=org,
            requirement__framework__jurisdiction=jurisdiction,
        ).prefetch_related('requirement__templates')
    }

    category_labels = dict(RequirementCategory.choices)
    grouped = defaultdict(list)
    totals = {'total': 0, 'done': 0, 'weight_total': 0, 'weight_done': 0}
    for ra in applicable:
        req = ra.requirement
        ctrl = controls.get(req.id)
        templates = list(req.templates.all())
        grouped[req.category].append({
            'req': req,
            'control': ctrl,
            'templates': templates,
            'status': ctrl.status if ctrl else ControlStatus.NOT_STARTED,
            'progress': ctrl.progress_weight if ctrl else 0,
        })
        totals['total'] += 1
        totals['weight_total'] += req.severity_weight
        if ctrl and ctrl.is_done:
            totals['done'] += 1
            totals['weight_done'] += req.severity_weight

    grouped_sorted = [
        {'code': code, 'label': category_labels.get(code, code), 'items': items}
        for code, items in grouped.items()
    ]

    score = round(
        100 * totals['weight_done'] / totals['weight_total']
    ) if totals['weight_total'] else 0

    return render(request, 'compliance/jurisdiction.html', {
        'jurisdiction': jurisdiction,
        'grouped': grouped_sorted,
        'score': score,
        'total': totals['total'],
        'done': totals['done'],
    })


@login_required
def compliance_advance(request, control_id):
    """Advance a control to the next state (Not started → In progress → Implemented)."""
    if request.method != 'POST':
        return HttpResponseBadRequest('POST only')
    org = request.active_org
    control = get_object_or_404(Control, pk=control_id, organization=org)
    direction = request.POST.get('to')
    if direction in [s for s, _ in ControlStatus.choices]:
        control.status = direction
    else:
        try:
            idx = STATUS_ORDER.index(control.status)
            control.status = STATUS_ORDER[(idx + 1) % len(STATUS_ORDER)]
        except ValueError:
            control.status = ControlStatus.IN_PROGRESS
    if control.is_done and not control.completed_at:
        control.completed_at = timezone.now()
    elif not control.is_done:
        control.completed_at = None
    control.save()
    messages.success(request, f'{control.requirement.code} → {control.get_status_display()}')
    return redirect(
        'compliance:jurisdiction',
        code=control.requirement.framework.jurisdiction.code,
    )
