from django.test import TestCase
import factories
from rest_framework.test import APIClient


class BrowsableAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.tola_user = factories.CoreUser()

    def test_login_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.set_password('1234')
        self.tola_user.user.save()

        self.client.login(username=self.tola_user.user.username,
                          password='1234')
        response = self.client.get('/api/docs/')

        self.assertEqual(response.status_code, 200)

    def test_login_normaluser(self):
        self.tola_user.user.set_password('1234')
        self.tola_user.user.save()

        self.client.login(username=self.tola_user.user.username,
                          password='1234')
        response = self.client.get('/api/docs/')

        self.assertEqual(response.status_code, 403)
