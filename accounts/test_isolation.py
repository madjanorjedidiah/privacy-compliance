"""Multi-tenant isolation guarantees.

Critical: user in org A must never see or mutate data in org B.
"""
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Membership, Organization, OrgProfile
from assessments.services import run_assessment
from controls.models import Control
from controls.services import sync_controls_from_assessment
from risks.models import Risk


class TenantIsolationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def _org(self, name, country):
        org = Organization.objects.create(name=name, country=country, onboarded_at=timezone.now())
        OrgProfile.objects.create(
            organization=org,
            data_subject_locations=[country],
            data_categories=['contact'],
        )
        return org

    def setUp(self):
        User = get_user_model()
        self.user_a = User.objects.create_user(username='alice', password='pw-alpha-123!', display_name='Alice')
        self.user_b = User.objects.create_user(username='bob', password='pw-beta-123!', display_name='Bob')
        self.org_a = self._org('Acme GH', 'GH')
        self.org_b = self._org('Beta KE', 'KE')
        Membership.objects.create(user=self.user_a, organization=self.org_a, role='owner', is_primary=True)
        Membership.objects.create(user=self.user_b, organization=self.org_b, role='owner', is_primary=True)

        sync_controls_from_assessment(self.org_a, run_assessment(self.org_a))
        sync_controls_from_assessment(self.org_b, run_assessment(self.org_b))

        self.b_control = Control.objects.filter(organization=self.org_b).first()
        self.b_risk = Risk.objects.create(organization=self.org_b, title='B secret risk', likelihood=3, impact=3)

    def _login(self, username, password):
        c = Client()
        c.login(username=username, password=password)
        return c

    def test_control_detail_cross_org_returns_404(self):
        c = self._login('alice', 'pw-alpha-123!')
        resp = c.get(reverse('controls:detail', kwargs={'pk': self.b_control.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_risk_edit_cross_org_returns_404(self):
        c = self._login('alice', 'pw-alpha-123!')
        resp = c.get(reverse('risks:edit', kwargs={'pk': self.b_risk.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_compliance_advance_cross_org_returns_404(self):
        c = self._login('alice', 'pw-alpha-123!')
        resp = c.post(reverse('compliance:advance', kwargs={'control_id': self.b_control.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_dashboard_shows_only_own_org_data(self):
        c = self._login('alice', 'pw-alpha-123!')
        resp = c.get(reverse('dashboard:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Acme GH')
        self.assertNotContains(resp, 'B secret risk')

    def test_form_dropdowns_do_not_leak_other_org_users(self):
        """Regression: ModelChoiceField querysets on every *form* must be
        narrowed to the active org. Without that, a viewer in org A sees
        user B in org B via the HTML <select>."""
        from ropa.models import ProcessingActivity  # noqa

        c = self._login('alice', 'pw-alpha-123!')
        resp = c.get(reverse('ropa:create'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Alice')
        self.assertNotContains(resp, 'Bob')

    def test_form_dropdowns_do_not_leak_other_org_retention_policies(self):
        from retention.models import RetentionPolicy
        RetentionPolicy.objects.create(
            organization=self.org_b, name='Org B financial records',
            data_category='financial', retention_months=36,
        )
        c = self._login('alice', 'pw-alpha-123!')
        resp = c.get(reverse('ropa:create'))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, 'Org B financial records')


class DPORegisterIsolationTests(TestCase):
    """Detail/edit views for every DPO register must return 404 across orgs."""

    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def setUp(self):
        User = get_user_model()
        self.user_a = User.objects.create_user(username='alice', password='pw-alpha-123!', display_name='Alice')
        self.user_b = User.objects.create_user(username='bob', password='pw-beta-123!', display_name='Bob')
        self.org_a = Organization.objects.create(name='Acme', country='GH', onboarded_at=timezone.now())
        self.org_b = Organization.objects.create(name='Beta', country='KE', onboarded_at=timezone.now())
        OrgProfile.objects.create(organization=self.org_a)
        OrgProfile.objects.create(organization=self.org_b)
        Membership.objects.create(user=self.user_a, organization=self.org_a, role='owner', is_primary=True)
        Membership.objects.create(user=self.user_b, organization=self.org_b, role='owner', is_primary=True)

        from ropa.models import ProcessingActivity
        from retention.models import RetentionPolicy
        from dpia.models import DPIA
        from vendors.models import Vendor

        self.b_activity = ProcessingActivity.objects.create(organization=self.org_b, name='B payroll')
        self.b_policy = RetentionPolicy.objects.create(
            organization=self.org_b, name='B records', data_category='contact', retention_months=12,
        )
        self.b_dpia = DPIA.objects.create(organization=self.org_b, title='B profiling')
        self.b_vendor = Vendor.objects.create(organization=self.org_b, name='B CRM', country='US')

    def _login_a(self):
        c = Client()
        c.login(username='alice', password='pw-alpha-123!')
        return c

    def test_ropa_detail_cross_org(self):
        resp = self._login_a().get(reverse('ropa:detail', kwargs={'pk': self.b_activity.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_ropa_edit_cross_org(self):
        resp = self._login_a().get(reverse('ropa:edit', kwargs={'pk': self.b_activity.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_retention_edit_cross_org(self):
        resp = self._login_a().get(reverse('retention:edit', kwargs={'pk': self.b_policy.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_dpia_detail_cross_org(self):
        resp = self._login_a().get(reverse('dpia:detail', kwargs={'pk': self.b_dpia.pk}))
        self.assertEqual(resp.status_code, 404)

    def test_vendor_edit_cross_org(self):
        resp = self._login_a().get(reverse('vendors:edit', kwargs={'pk': self.b_vendor.pk}))
        self.assertEqual(resp.status_code, 404)


class RoleEnforcementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def setUp(self):
        User = get_user_model()
        self.viewer = User.objects.create_user(username='viewer', password='viewerpw-123!')
        self.org = Organization.objects.create(name='RO Co', country='GH', onboarded_at=timezone.now())
        OrgProfile.objects.create(organization=self.org, data_subject_locations=['GH'], data_categories=['contact'])
        Membership.objects.create(user=self.viewer, organization=self.org, role='viewer', is_primary=True)
        sync_controls_from_assessment(self.org, run_assessment(self.org))

    def test_viewer_can_get_compliance_pages(self):
        c = Client()
        c.login(username='viewer', password='viewerpw-123!')
        self.assertEqual(c.get(reverse('compliance:home')).status_code, 200)
        self.assertEqual(c.get(reverse('ropa:list')).status_code, 200)

    def test_viewer_cannot_post_to_advance(self):
        c = Client()
        c.login(username='viewer', password='viewerpw-123!')
        control = Control.objects.filter(organization=self.org).first()
        resp = c.post(reverse('compliance:advance', kwargs={'control_id': control.pk}), data={'to': 'in_progress'})
        self.assertEqual(resp.status_code, 403)
