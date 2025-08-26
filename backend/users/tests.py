from django.test import TestCase, Client
from rest_framework.test import APIClient


class HealthEndpointTests(TestCase):
	def setUp(self):
		self.client = APIClient()

	def test_health_ok(self):
		# Use secure flag to avoid HTTP->HTTPS redirect (301) under SECURE_SSL_REDIRECT
		resp = self.client.get('/api/health/', secure=True)
		self.assertEqual(resp.status_code, 200, f"Unexpected status {resp.status_code}; body={getattr(resp,'content',b'')[:200]}")
		data = resp.json()
		self.assertIn('status', data)
		self.assertIn('mongo', data)  # field present even if error/degraded

	def test_root_lists_versioned_alias(self):
		resp = self.client.get('/', secure=True)
		self.assertEqual(resp.status_code, 200, f"Unexpected status {resp.status_code}")
		data = resp.json()
		self.assertIn('endpoints', data)
		self.assertIn('api_v1_root', data['endpoints'])


class RootViewTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_root_view_structure(self):
		resp = self.client.get('/', secure=True)
		self.assertEqual(resp.status_code, 200, f"Unexpected status {resp.status_code}")
		data = resp.json()
		self.assertIn('message', data)
		self.assertIn('endpoints', data)
		self.assertIn('version', data)
		self.assertIn('auth', data['endpoints'])
		self.assertIn('documents', data['endpoints'])
		self.assertIn('chat', data['endpoints'])
