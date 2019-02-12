from django.test import TestCase
import factories
from rest_framework.test import APIClient


class BrowsableAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.core_user = factories.CoreUser()

    def test_normaluser(self):
        response = self.client.get('/docs/')
        self.assertEqual(response.status_code, 200)
