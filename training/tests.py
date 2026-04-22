from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import Organization
from training.models import TrainingModule, TrainingRecord


class TrainingRecordTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Y', country='GH')
        self.user = get_user_model().objects.create_user(username='alice', password='pw-321-ok!')
        self.module = TrainingModule.objects.create(
            organization=self.org, name='Data Protection 101', required_months=12,
        )

    def test_expiry_defaults_to_module_window(self):
        r = TrainingRecord.objects.create(module=self.module, user=self.user, completed_on=date.today())
        self.assertIsNotNone(r.expires_on)
        self.assertGreater(r.expires_on, date.today())

    def test_is_expired_when_in_past(self):
        r = TrainingRecord.objects.create(
            module=self.module, user=self.user,
            completed_on=date.today() - timedelta(days=500),
        )
        self.assertTrue(r.is_expired)
