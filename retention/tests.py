from django.test import TestCase

from accounts.models import Organization
from retention.models import RetentionPolicy


class RetentionPolicyTests(TestCase):
    def test_policy_stores_and_lists(self):
        org = Organization.objects.create(name='X', country='NG')
        p = RetentionPolicy.objects.create(
            organization=org, name='KYC records', data_category='government_id',
            retention_months=72, legal_basis='AML Act §18',
        )
        self.assertEqual(str(p), 'KYC records (Government-issued ID)')
        self.assertEqual(RetentionPolicy.objects.filter(organization=org).count(), 1)
