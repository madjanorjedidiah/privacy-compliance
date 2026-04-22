from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import Membership, Organization, OrgProfile
from ropa.models import LawfulBasis, ProcessingActivity


class ProcessingActivityTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='dpo', password='pw-secret-99!', display_name='DPO')
        self.org = Organization.objects.create(name='Acme', country='GH', onboarded_at=timezone.now())
        OrgProfile.objects.create(organization=self.org)
        Membership.objects.create(user=self.user, organization=self.org, role='owner', is_primary=True)

    def test_create_activity(self):
        a = ProcessingActivity.objects.create(
            organization=self.org,
            name='Customer onboarding',
            lawful_basis=LawfulBasis.CONTRACT,
            data_categories=['contact', 'government_id'],
            data_subject_categories=['customers'],
            recipients=['Treasury Ops'],
        )
        self.assertEqual(str(a), 'Customer onboarding')

    def test_invalid_data_category_rejected(self):
        a = ProcessingActivity(
            organization=self.org, name='Bad', data_categories=['pwned'],
        )
        with self.assertRaises(ValidationError):
            a.full_clean()

    def test_ropa_list_page_renders(self):
        c = Client()
        c.login(username='dpo', password='pw-secret-99!')
        resp = c.get(reverse('ropa:list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Record of Processing Activities')
