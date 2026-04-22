from django.db import transaction

from assessments.models import RequirementApplicability
from assessments.services import latest_assessment
from core.choices import ControlStatus

from .models import Control


@transaction.atomic
def sync_controls_from_assessment(organization, assessment=None):
    """Synchronise Controls to the latest applicability assessment.

    - Creates controls for newly-applicable requirements.
    - Marks previously-applicable controls as NOT_APPLICABLE when the
      requirement is no longer applicable AND the user hasn't recorded
      any progress (status is still NOT_STARTED). This keeps the compliance
      score honest without destroying user-entered work.
    - Deletes controls that are both no-longer-applicable AND untouched
      (no evidence, no completed_at, no notes) so they don't clutter.

    Returns dict of counts for the caller.
    """
    assessment = assessment or latest_assessment(organization)
    if not assessment:
        return {'created': 0, 'deprecated': 0, 'removed': 0}

    applicable_req_ids = set(
        RequirementApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .values_list('requirement_id', flat=True)
    )

    created = 0
    for req_id in applicable_req_ids:
        _, was_created = Control.objects.get_or_create(
            organization=organization,
            requirement_id=req_id,
        )
        if was_created:
            created += 1

    stale = (
        Control.objects
        .filter(organization=organization)
        .exclude(requirement_id__in=applicable_req_ids)
    )
    deprecated = 0
    removed = 0
    for ctrl in stale:
        # Delete truly untouched controls; keep the record for any that have
        # human progress or evidence so the historical trail is preserved.
        has_evidence = ctrl.evidence.exists()
        untouched = (
            ctrl.status == ControlStatus.NOT_STARTED
            and not ctrl.notes
            and not ctrl.completed_at
            and not has_evidence
        )
        if untouched:
            ctrl.delete()
            removed += 1
        else:
            ctrl.status = ControlStatus.NOT_APPLICABLE
            if not ctrl.notes:
                ctrl.notes = 'Marked not applicable after the organisation profile changed.'
            ctrl.save(update_fields=['status', 'notes', 'updated_at'])
            deprecated += 1

    return {'created': created, 'deprecated': deprecated, 'removed': removed}
