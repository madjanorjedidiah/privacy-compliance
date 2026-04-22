from django.core.management import call_command
from django.test import TestCase

from accounts.models import Organization, OrgProfile
from assessments.services import latest_assessment, run_assessment
from assessments.models import FrameworkApplicability
from controls.services import sync_controls_from_assessment
from controls.models import Control


class AssessmentFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def _setup_org(self, **profile_kwargs):
        org = Organization.objects.create(name='Kudu Fintech', country='GH', revenue_band='10-25M')
        profile_defaults = dict(
            data_subject_locations=['GH', 'DE'],
            data_categories=['contact', 'financial'],
            cross_border_transfers=True,
            annual_data_subjects_estimate=50_000,
        )
        profile_defaults.update(profile_kwargs)
        OrgProfile.objects.create(organization=org, **profile_defaults)
        return org

    def test_run_assessment_persists_framework_results(self):
        org = self._setup_org()
        assessment = run_assessment(org)
        self.assertEqual(latest_assessment(org).pk, assessment.pk)
        gdpr_fa = FrameworkApplicability.objects.get(assessment=assessment, framework__code='GDPR')
        ghana_fa = FrameworkApplicability.objects.get(assessment=assessment, framework__code='GH-DPA-2012')
        ccpa_fa = FrameworkApplicability.objects.get(assessment=assessment, framework__code='US-CCPA')
        self.assertTrue(gdpr_fa.applicable)
        self.assertTrue(ghana_fa.applicable)
        self.assertFalse(ccpa_fa.applicable)

    def test_controls_created_for_applicable_requirements(self):
        org = self._setup_org()
        assessment = run_assessment(org)
        result = sync_controls_from_assessment(org, assessment)
        self.assertGreater(result['created'], 0)
        self.assertEqual(result['created'], Control.objects.filter(organization=org).count())

    def test_ccpa_opt_out_not_created_when_no_california(self):
        org = self._setup_org(offers_to_california_residents=False)
        assessment = run_assessment(org)
        sync_controls_from_assessment(org, assessment)
        self.assertFalse(Control.objects.filter(organization=org, requirement__code='CCPA-OptOut').exists())

    def test_stale_controls_deprecated_when_applicability_shrinks(self):
        from core.choices import ControlStatus
        org = self._setup_org()
        a1 = run_assessment(org)
        sync_controls_from_assessment(org, a1)
        before = Control.objects.filter(organization=org).count()
        self.assertGreater(before, 0)

        # User narrows profile: drop EU subjects and California
        org.profile.data_subject_locations = ['GH']
        org.profile.offers_to_california_residents = False
        org.profile.save()

        # Record progress on one control so it doesn't get deleted silently
        ctrl = Control.objects.filter(organization=org).first()
        ctrl.status = ControlStatus.IN_PROGRESS
        ctrl.notes = 'Draft published'
        ctrl.save()

        a2 = run_assessment(org)
        result = sync_controls_from_assessment(org, a2)
        self.assertGreater(result['removed'] + result['deprecated'], 0)
        # The touched control must still exist but should never be deleted.
        self.assertTrue(Control.objects.filter(pk=ctrl.pk).exists())
