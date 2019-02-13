from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase

from .. import views


class IndexViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_dispatch_unauthenticated(self):
        request = self.factory.get('', follow=True)
        request.user = AnonymousUser()
        response = views.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = str(response.render().content)
        self.assertIn('href="/api/docs"', template_content)


class HealthCheckViewTest(TestCase):
    def test_health_check_success(self):
        c = Client()
        response = c.get('/health_check/')
        self.assertEqual(response.status_code, 200)
