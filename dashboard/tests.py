from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Membership, Organization, OrgProfile
from assessments.services import run_assessment
from controls.services import sync_controls_from_assessment
from dashboard.services import gap_map, kpi_snapshot, maturity_per_framework


class DashboardServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def setUp(self):
        self.org = Organization.objects.create(name='Kudu', country='KE', revenue_band='1-10M')
        OrgProfile.objects.create(
            organization=self.org,
            data_subject_locations=['KE', 'NG'],
            data_categories=['contact'],
            cross_border_transfers=False,
        )
        assessment = run_assessment(self.org)
        sync_controls_from_assessment(self.org, assessment)

    def test_kpi_snapshot_shape(self):
        kpis = kpi_snapshot(self.org)
        for key in ('maturity', 'total_controls', 'open_controls', 'overdue_controls',
                    'total_risks', 'critical_risks', 'open_dsars', 'open_incidents'):
            self.assertIn(key, kpis)
        self.assertGreater(kpis['total_controls'], 0)

    def test_maturity_per_framework_present(self):
        rows = maturity_per_framework(self.org)
        codes = {r['framework'].code for r in rows}
        self.assertIn('KE-DPA-2019', codes)
        self.assertIn('NG-NDPA-2023', codes)
        self.assertNotIn('GDPR', codes)

    def test_gap_map_has_grid(self):
        data = gap_map(self.org)
        self.assertTrue(data['grid'])
        self.assertTrue(data['categories'])


class DashboardViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('seed_jurisdictions')

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='jane', password='password-xyz-8', display_name='Jane')
        self.org = Organization.objects.create(name='Kudu', country='KE', onboarded_at=timezone.now())
        OrgProfile.objects.create(
            organization=self.org,
            data_subject_locations=['KE'],
            data_categories=['contact'],
        )
        Membership.objects.create(user=self.user, organization=self.org, role='owner', is_primary=True)
        assessment = run_assessment(self.org, user=self.user)
        sync_controls_from_assessment(self.org, assessment)
        self.client = Client()
        self.client.login(username='jane', password='password-xyz-8')

    def test_dashboard_home_renders(self):
        resp = self.client.get(reverse('dashboard:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Command Center')

    def test_gap_map_renders(self):
        resp = self.client.get(reverse('dashboard:gap_map'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Gap Map')

    def test_controls_list_renders(self):
        resp = self.client.get(reverse('controls:list'))
        self.assertEqual(resp.status_code, 200)

    def test_risks_list_renders(self):
        resp = self.client.get(reverse('risks:list'))
        self.assertEqual(resp.status_code, 200)

    def test_templates_list_renders(self):
        resp = self.client.get(reverse('templates:list'))
        self.assertEqual(resp.status_code, 200)

    def test_jurisdictions_list_renders(self):
        resp = self.client.get(reverse('jurisdictions:list'))
        self.assertEqual(resp.status_code, 200)
