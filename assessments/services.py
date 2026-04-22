from django.db import transaction
from django.utils import timezone

from jurisdictions.applicability import framework_applies, requirement_applies
from jurisdictions.models import Framework, Requirement

from .models import Assessment, FrameworkApplicability, RequirementApplicability


@transaction.atomic
def run_assessment(organization, user=None, name='Applicability assessment'):
    """Run the applicability engine for the organization and persist results."""
    profile = organization.profile

    snapshot = {
        'sectors': profile.sectors,
        'data_categories': profile.data_categories,
        'processing_purposes': profile.processing_purposes,
        'data_subject_locations': profile.data_subject_locations,
        'has_establishment_in': profile.has_establishment_in,
        'processes_eu_residents': profile.processes_eu_residents,
        'offers_to_california_residents': profile.offers_to_california_residents,
        'cross_border_transfers': profile.cross_border_transfers,
        'uses_automated_decision_making': profile.uses_automated_decision_making,
        'processes_childrens_data': profile.processes_childrens_data,
        'processes_health_data': profile.processes_health_data,
        'processes_biometric_data': profile.processes_biometric_data,
        'annual_data_subjects_estimate': profile.annual_data_subjects_estimate,
        'captured_at': timezone.now().isoformat(),
    }

    assessment = Assessment.objects.create(
        organization=organization, run_by=user, name=name, profile_snapshot=snapshot,
    )

    for framework in Framework.objects.select_related('jurisdiction').all():
        fw_result = framework_applies(profile, framework.code)
        FrameworkApplicability.objects.create(
            assessment=assessment,
            framework=framework,
            applicable=fw_result.applicable,
            rationale=fw_result.rationale,
        )
        if not fw_result.applicable:
            for req in framework.requirements.all():
                RequirementApplicability.objects.create(
                    assessment=assessment,
                    requirement=req,
                    applicable=False,
                    rationale='Framework not applicable to this organization.',
                )
            continue
        for req in framework.requirements.all():
            r_result = requirement_applies(req, profile)
            RequirementApplicability.objects.create(
                assessment=assessment,
                requirement=req,
                applicable=r_result.applicable,
                rationale=r_result.rationale,
            )

    return assessment


def latest_assessment(organization):
    return (
        Assessment.objects
        .filter(organization=organization)
        .order_by('-run_at')
        .first()
    )
