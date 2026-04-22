from django.test import TestCase

from accounts.models import Organization
from dpia.models import DPIA


class DPIATriggerTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Clinic', country='KE')

    def test_single_trigger_not_required(self):
        d = DPIA(organization=self.org, title='Trial', trigger_children=True)
        self.assertEqual(d.triggers_fired, 1)
        self.assertFalse(d.is_dpia_required)

    def test_two_triggers_required(self):
        d = DPIA(
            organization=self.org, title='Clinical trial',
            trigger_children=True, trigger_vulnerable_subjects=True,
        )
        self.assertEqual(d.triggers_fired, 2)
        self.assertTrue(d.is_dpia_required)

    def test_residual_below_inherent(self):
        d = DPIA.objects.create(
            organization=self.org, title='Profiling',
            inherent_likelihood=5, inherent_impact=5,
            residual_likelihood=2, residual_impact=3,
        )
        self.assertEqual(d.inherent_score, 25)
        self.assertEqual(d.residual_score, 6)
