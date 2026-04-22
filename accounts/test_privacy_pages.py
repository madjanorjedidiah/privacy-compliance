"""Tests for the public privacy / terms / cookies pages and GDPR self-service."""
import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import AuthEvent, Membership, Organization, OrgProfile


class PublicPagesTests(TestCase):
    def test_privacy_page_renders(self):
        resp = self.client.get(reverse('public:privacy'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Privacy Notice')
        self.assertContains(resp, 'Data Protection Act, 2012')

    def test_terms_page_renders(self):
        resp = self.client.get(reverse('public:terms'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Terms of Service')

    def test_cookies_page_renders(self):
        resp = self.client.get(reverse('public:cookies'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'strictly necessary')


class SelfServiceDataRightsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='alice', password='password-xyz-98!',
            email='alice@example.test', display_name='Alice',
        )
        self.org = Organization.objects.create(name='Acme', country='GH')
        OrgProfile.objects.create(organization=self.org)
        Membership.objects.create(user=self.user, organization=self.org, role='owner', is_primary=True)
        self.client = Client()
        self.client.login(username='alice', password='password-xyz-98!')

    def test_export_returns_json_with_account_fields(self):
        resp = self.client.post(reverse('accounts:export_me'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/json; charset=utf-8')
        body = json.loads(resp.content)
        self.assertEqual(body['user']['username'], 'alice')
        self.assertEqual(body['user']['email'], 'alice@example.test')
        self.assertEqual(body['memberships'][0]['organization'], 'Acme')
        # Export should itself be logged as an AuthEvent
        self.assertTrue(
            AuthEvent.objects.filter(user=self.user, kind=AuthEvent.Kind.DATA_EXPORT).exists()
        )

    def test_account_deletion_blocked_for_sole_owner(self):
        resp = self.client.post(
            reverse('accounts:delete_me'), data={'confirm': 'alice'}, follow=True,
        )
        # Sole-owner guard — account must not be deleted.
        self.assertTrue(get_user_model().objects.filter(username='alice').exists())

    def test_account_deletion_succeeds_with_co_owner(self):
        User = get_user_model()
        co = User.objects.create_user(username='bob', password='co-owner-pw-1!', email='bob@example.test')
        Membership.objects.create(user=co, organization=self.org, role='owner')

        resp = self.client.post(reverse('accounts:delete_me'), data={'confirm': 'alice'}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(User.objects.filter(username='alice').exists())
        self.assertTrue(
            AuthEvent.objects.filter(kind=AuthEvent.Kind.ACCOUNT_DELETE, username_attempted='alice').exists()
        )


class AuthEventSignalTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='charlie', password='charliepw-321!')

    def test_successful_login_creates_event(self):
        c = Client()
        ok = c.login(username='charlie', password='charliepw-321!')
        self.assertTrue(ok)
        # Django's login() sends user_logged_in when used via the auth views,
        # but Client.login doesn't. Drive it through the real LoginView.
        c.logout()
        resp = c.post(
            reverse('accounts:login'),
            {'username': 'charlie', 'password': 'charliepw-321!'},
            follow=False,
        )
        self.assertIn(resp.status_code, (200, 302))
        self.assertTrue(AuthEvent.objects.filter(user=self.user, kind=AuthEvent.Kind.LOGIN_OK).exists())

    def test_failed_login_creates_event(self):
        c = Client()
        c.post(
            reverse('accounts:login'),
            {'username': 'charlie', 'password': 'wrong-password-!!'},
        )
        self.assertTrue(
            AuthEvent.objects.filter(kind=AuthEvent.Kind.LOGIN_FAIL, username_attempted='charlie').exists()
        )
