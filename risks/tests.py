from django.test import TestCase

from accounts.models import Organization
from core.choices import Severity
from risks.models import Risk


class RiskScoringTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Acme', country='GH')

    def _risk(self, **kwargs):
        return Risk.objects.create(organization=self.org, title='R', **kwargs)

    def test_low_risk_scores_low(self):
        r = self._risk(likelihood=1, impact=1, data_sensitivity=1, data_volume_log10=2, regulator_activity=1, control_effectiveness=90)
        self.assertEqual(r.severity, Severity.INFO)

    def test_high_risk_scores_high(self):
        r = self._risk(likelihood=5, impact=5, data_sensitivity=5, data_volume_log10=6, regulator_activity=5, control_effectiveness=10)
        self.assertIn(r.severity, {Severity.CRITICAL, Severity.HIGH})

    def test_control_effectiveness_reduces_residual(self):
        r_low = self._risk(likelihood=4, impact=4, control_effectiveness=10)
        r_high = self._risk(likelihood=4, impact=4, control_effectiveness=90)
        self.assertGreater(r_low.residual_score, r_high.residual_score)
