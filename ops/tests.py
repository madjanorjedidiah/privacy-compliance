from django.test import TestCase


class HealthEndpointTests(TestCase):
    def test_health_returns_200(self):
        resp = self.client.get('/ops/health/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()['status'], 'alive')

    def test_readyz_returns_200(self):
        resp = self.client.get('/ops/readyz/')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['status'], 'ready')
        self.assertEqual(body['checks']['database'], 'ok')
