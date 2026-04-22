from datetime import date, timedelta

from django.test import TestCase

from accounts.models import Organization
from vendors.models import Vendor


class VendorLifecycleTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Z', country='NG')

    def test_dpa_expired_flag(self):
        v = Vendor.objects.create(
            organization=self.org, name='CRM.io', country='US',
            dpa_on_file=True, dpa_expires_on=date.today() - timedelta(days=10),
        )
        self.assertTrue(v.dpa_expired)

    def test_dpa_expiring_soon_flag(self):
        v = Vendor.objects.create(
            organization=self.org, name='Analytics.io', country='US',
            dpa_on_file=True, dpa_expires_on=date.today() + timedelta(days=30),
        )
        self.assertTrue(v.dpa_expiring_soon)
        self.assertFalse(v.dpa_expired)

    def test_no_dpa_flags(self):
        v = Vendor.objects.create(organization=self.org, name='No DPA', country='GH')
        self.assertFalse(v.dpa_expiring_soon)
        self.assertFalse(v.dpa_expired)
