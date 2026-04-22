from django.db import transaction

from assessments.models import RequirementApplicability
from assessments.services import latest_assessment

from .models import Control


@transaction.atomic
def sync_controls_from_assessment(organization, assessment=None):
    """Create a Control row for every applicable Requirement in the latest assessment."""
    assessment = assessment or latest_assessment(organization)
    if not assessment:
        return 0

    applicable_reqs = (
        RequirementApplicability.objects
        .filter(assessment=assessment, applicable=True)
        .select_related('requirement')
    )

    created = 0
    for ra in applicable_reqs:
        _, was_created = Control.objects.get_or_create(
            organization=organization,
            requirement=ra.requirement,
        )
        if was_created:
            created += 1
    return created
