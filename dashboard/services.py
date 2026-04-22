"""
Dashboard aggregations: KPIs, maturity score, gap map, top risks.
"""
from collections import defaultdict

from django.db.models import Avg, Count, Q

from assessments.models import FrameworkApplicability, RequirementApplicability
from assessments.services import latest_assessment
from controls.models import Control
from core.choices import ControlStatus, Severity
from dsar.models import DSARRequest
from incidents.models import Incident
from jurisdictions.models import Framework, Jurisdiction, RequirementCategory
from risks.models import Risk


def weighted_maturity(organization):
    """Severity-weighted compliance score across all applicable requirements."""
    assessment = latest_assessment(organization)
    if not assessment:
        return {'score': 0, 'total_requirements': 0, 'done_requirements': 0, 'weight_total': 0, 'weight_done': 0}

    applicable = (
        RequirementApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .select_related('requirement')
    )
    controls_by_req = {
        c.requirement_id: c for c in Control.objects.filter(organization=organization)
    }

    weight_total = 0
    weight_done = 0
    total = 0
    done = 0
    for ra in applicable:
        req = ra.requirement
        ctrl = controls_by_req.get(req.id)
        weight = max(1, req.severity_weight)
        weight_total += weight
        total += 1
        progress = (ctrl.progress_weight / 100) if ctrl else 0
        weight_done += weight * progress
        if ctrl and ctrl.is_done:
            done += 1

    score = round(100 * weight_done / weight_total) if weight_total else 0
    return {
        'score': score,
        'total_requirements': total,
        'done_requirements': done,
        'weight_total': weight_total,
        'weight_done': round(weight_done, 2),
    }


def jurisdiction_scorecard(organization):
    """Return one row per jurisdiction that has applicable requirements, with weighted score."""
    assessment = latest_assessment(organization)
    if not assessment:
        return []

    applicable = (
        RequirementApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .select_related('requirement__framework__jurisdiction')
    )
    controls_by_req = {
        c.requirement_id: c for c in Control.objects.filter(organization=organization)
    }

    buckets = {}
    for ra in applicable:
        req = ra.requirement
        jur = req.framework.jurisdiction
        ctrl = controls_by_req.get(req.id)
        b = buckets.setdefault(jur.code, {
            'jurisdiction': jur,
            'frameworks': set(),
            'total': 0, 'done': 0, 'in_progress': 0, 'not_started': 0,
            'weight_total': 0, 'weight_done': 0,
        })
        b['frameworks'].add(req.framework.short_name)
        b['total'] += 1
        weight = max(1, req.severity_weight)
        b['weight_total'] += weight
        progress = (ctrl.progress_weight / 100) if ctrl else 0
        b['weight_done'] += weight * progress
        if ctrl and ctrl.is_done:
            b['done'] += 1
        elif ctrl and ctrl.status == ControlStatus.IN_PROGRESS:
            b['in_progress'] += 1
        else:
            b['not_started'] += 1

    rows = []
    for code, b in buckets.items():
        score = round(100 * b['weight_done'] / b['weight_total']) if b['weight_total'] else 0
        rows.append({
            'jurisdiction': b['jurisdiction'],
            'frameworks': sorted(b['frameworks']),
            'total': b['total'],
            'done': b['done'],
            'in_progress': b['in_progress'],
            'not_started': b['not_started'],
            'score': score,
        })
    rows.sort(key=lambda r: r['jurisdiction'].name)
    return rows


def maturity_per_framework(organization):
    """Return list of dicts: framework, total, done, progress (0-100)."""
    assessment = latest_assessment(organization)
    result = []
    if not assessment:
        return result

    applicable = (
        RequirementApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .select_related('requirement__framework__jurisdiction')
    )
    bucket = defaultdict(list)
    for ra in applicable:
        bucket[ra.requirement.framework_id].append(ra.requirement_id)

    controls_by_req = {
        c.requirement_id: c for c in
        Control.objects.filter(organization=organization)
    }

    for fw_id, req_ids in bucket.items():
        framework = Framework.objects.select_related('jurisdiction').get(pk=fw_id)
        scores = []
        done = 0
        for rid in req_ids:
            ctrl = controls_by_req.get(rid)
            if ctrl:
                scores.append(ctrl.progress_weight)
                if ctrl.is_done:
                    done += 1
            else:
                scores.append(0)
        progress = round(sum(scores) / len(scores)) if scores else 0
        result.append({
            'framework': framework,
            'total': len(req_ids),
            'done': done,
            'progress': progress,
        })
    result.sort(key=lambda r: r['framework'].short_name)
    return result


def overall_maturity(organization):
    rows = maturity_per_framework(organization)
    if not rows:
        return 0
    return round(sum(r['progress'] for r in rows) / len(rows))


def kpi_snapshot(organization):
    controls = Control.objects.filter(organization=organization)
    risks = Risk.objects.filter(organization=organization)
    dsars = DSARRequest.objects.filter(organization=organization)
    incidents = Incident.objects.filter(organization=organization)

    open_controls = controls.exclude(
        status__in=[ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED, ControlStatus.NOT_APPLICABLE]
    ).count()
    overdue_controls = controls.filter(due_date__isnull=False).exclude(
        status__in=[ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED, ControlStatus.NOT_APPLICABLE]
    ).extra(where=['due_date < date("now")']).count()
    critical_risks = risks.filter(severity__in=[Severity.CRITICAL, Severity.HIGH]).count()

    weighted = weighted_maturity(organization)
    return {
        'maturity': weighted['score'],
        'weighted_done': weighted['done_requirements'],
        'weighted_total': weighted['total_requirements'],
        'total_controls': controls.count(),
        'open_controls': open_controls,
        'overdue_controls': overdue_controls,
        'total_risks': risks.count(),
        'critical_risks': critical_risks,
        'open_dsars': dsars.exclude(status=DSARRequest.Status.CLOSED).count(),
        'open_incidents': incidents.exclude(status=Incident.Status.RESOLVED).count(),
    }


def gap_map(organization):
    """Jurisdictions × RequirementCategory grid with coverage percent."""
    assessment = latest_assessment(organization)
    jurisdictions = list(Jurisdiction.objects.all())
    categories = [c for c in RequirementCategory.choices]

    grid = []
    controls_by_req = {
        c.requirement_id: c for c in Control.objects.filter(organization=organization)
    }

    for j in jurisdictions:
        row = {'jurisdiction': j, 'cells': []}
        fw_ids = list(Framework.objects.filter(jurisdiction=j).values_list('id', flat=True))
        for code, label in categories:
            if not assessment:
                row['cells'].append({'category_code': code, 'category_label': label, 'applicable': 0, 'coverage': None})
                continue
            applicable_reqs = (
                RequirementApplicability.objects
                .filter(assessment=assessment, applicable=True,
                        requirement__framework_id__in=fw_ids,
                        requirement__category=code)
                .values_list('requirement_id', flat=True)
            )
            total = len(applicable_reqs)
            if total == 0:
                row['cells'].append({'category_code': code, 'category_label': label, 'applicable': 0, 'coverage': None})
                continue
            progress_sum = 0
            for rid in applicable_reqs:
                ctrl = controls_by_req.get(rid)
                progress_sum += ctrl.progress_weight if ctrl else 0
            coverage = round(progress_sum / total)
            row['cells'].append({
                'category_code': code,
                'category_label': label,
                'applicable': total,
                'coverage': coverage,
            })
        grid.append(row)
    return {'categories': categories, 'grid': grid}


def top_risks(organization, limit=5):
    return list(
        Risk.objects.filter(organization=organization)
        .order_by('-residual_score')[:limit]
    )


def overdue_controls(organization, limit=5):
    return list(
        Control.objects
        .filter(organization=organization)
        .exclude(status__in=[ControlStatus.IMPLEMENTED, ControlStatus.VERIFIED, ControlStatus.NOT_APPLICABLE])
        .filter(due_date__isnull=False)
        .order_by('due_date')[:limit]
    )
