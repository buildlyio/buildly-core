from django.test import TestCase


class DocsViewTest(TestCase):
    def test_docs_success(self):
        response = self.client.get('/docs/')
        self.assertEqual(response.status_code, 200)
