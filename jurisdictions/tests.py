from django.core.management import call_command
from django.test import TestCase

from accounts.models import Organization, OrgProfile
from jurisdictions.applicability import framework_applies, requirement_applies
from jurisdictions.models import Framework, Requirement


class ApplicabilityEngineTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def _profile(self, **overrides):
        org_name = overrides.pop('org_name', 'Test Co')
        country = overrides.pop('country', 'GH')
        revenue_band = overrides.pop('revenue_band', '1-10M')
        org = Organization.objects.create(name=org_name, country=country, revenue_band=revenue_band)
        profile = OrgProfile.objects.create(organization=org)
        for k, v in overrides.items():
            setattr(profile, k, v)
        profile.save()
        return profile

    def test_gdpr_applies_to_eu_subjects(self):
        profile = self._profile(data_subject_locations=['DE', 'FR'])
        result = framework_applies(profile, 'GDPR')
        self.assertTrue(result.applicable)
        self.assertIn('EU/EEA residents', result.rationale)

    def test_gdpr_does_not_apply_to_ghana_only(self):
        profile = self._profile(data_subject_locations=['GH'])
        self.assertFalse(framework_applies(profile, 'GDPR').applicable)

    def test_ghana_dpa_applies(self):
        profile = self._profile(data_subject_locations=['GH'])
        self.assertTrue(framework_applies(profile, 'GH-DPA-2012').applicable)

    def test_ndpa_applies_with_ng_establishment(self):
        profile = self._profile(has_establishment_in=['NG'])
        self.assertTrue(framework_applies(profile, 'NG-NDPA-2023').applicable)

    def test_ccpa_requires_threshold(self):
        profile = self._profile(
            offers_to_california_residents=True,
            annual_data_subjects_estimate=1000,
            revenue_band='1-10M',
        )
        self.assertFalse(framework_applies(profile, 'US-CCPA').applicable)

    def test_ccpa_applies_on_volume(self):
        profile = self._profile(
            offers_to_california_residents=True,
            annual_data_subjects_estimate=200_000,
        )
        self.assertTrue(framework_applies(profile, 'US-CCPA').applicable)

    def test_dpia_rule(self):
        profile = self._profile(processes_health_data=True)
        dpia = Requirement.objects.get(code='GDPR-Art-35')
        result = requirement_applies(dpia, profile)
        self.assertTrue(result.applicable)

    def test_transfer_rule_off_when_no_transfers(self):
        profile = self._profile(cross_border_transfers=False)
        transfers = Requirement.objects.get(code='GDPR-Chap-V')
        self.assertFalse(requirement_applies(transfers, profile).applicable)

    def test_seed_counts(self):
        self.assertEqual(Framework.objects.count(), 5)
        self.assertGreaterEqual(Requirement.objects.count(), 30)
