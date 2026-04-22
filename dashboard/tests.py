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
        for key in ('maturity', 'weighted_done', 'weighted_total',
                    'total_controls', 'open_controls', 'overdue_controls',
                    'total_risks', 'critical_risks', 'open_dsars', 'open_incidents'):
            self.assertIn(key, kpis)
        self.assertGreater(kpis['total_controls'], 0)

    def test_kpi_snapshot_weighted_score_is_zero_on_fresh_workspace(self):
        kpis = kpi_snapshot(self.org)
        self.assertEqual(kpis['maturity'], 0)
        self.assertEqual(kpis['weighted_done'], 0)
        self.assertGreater(kpis['weighted_total'], 0)

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

    def test_weighted_score_rises_as_controls_implemented(self):
        from controls.models import Control
        from core.choices import ControlStatus
        before = kpi_snapshot(self.org)['maturity']
        self.assertEqual(before, 0)
        # Implement the highest-severity controls
        for c in Control.objects.filter(organization=self.org).order_by('-requirement__severity_weight')[:5]:
            c.status = ControlStatus.IMPLEMENTED
            c.save()
        after = kpi_snapshot(self.org)['maturity']
        self.assertGreater(after, before)


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

    def test_compliance_home_renders(self):
        resp = self.client.get(reverse('compliance:home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Compliance Checks')

    def test_compliance_jurisdiction_renders(self):
        resp = self.client.get(reverse('compliance:jurisdiction', kwargs={'code': 'KE'}))
        self.assertEqual(resp.status_code, 200)

    def test_quick_status_emits_audit_log(self):
        from controls.models import Control, ControlStatusChange
        control = Control.objects.filter(organization=self.org).first()
        self.assertEqual(ControlStatusChange.objects.filter(control=control).count(), 0)
        resp = self.client.post(
            reverse('controls:quick_status', kwargs={'pk': control.pk}),
            data={'status': 'in_progress'},
        )
        self.assertIn(resp.status_code, (200, 302))
        self.assertEqual(ControlStatusChange.objects.filter(control=control).count(), 1)

    def test_compliance_advance_cycles_status(self):
        from controls.models import Control
        from core.choices import ControlStatus
        control = Control.objects.filter(organization=self.org).first()
        self.assertEqual(control.status, ControlStatus.NOT_STARTED)

        resp = self.client.post(reverse('compliance:advance', kwargs={'control_id': control.pk}), data={'to': 'in_progress'})
        self.assertEqual(resp.status_code, 302)
        control.refresh_from_db()
        self.assertEqual(control.status, ControlStatus.IN_PROGRESS)

        resp = self.client.post(reverse('compliance:advance', kwargs={'control_id': control.pk}), data={'to': 'implemented'})
        self.assertEqual(resp.status_code, 302)
        control.refresh_from_db()
        self.assertEqual(control.status, ControlStatus.IMPLEMENTED)
        self.assertIsNotNone(control.completed_at)
