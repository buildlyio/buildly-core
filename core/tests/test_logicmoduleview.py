import factories

from django.test import TestCase
from rest_framework.test import APIClient


class LogicModuleViewsPermissionTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.core_user = factories.CoreUser()

        # bypass authentication
        self.client.force_authenticate(user=self.core_user)
        self.response_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': 1
        }

    def make_logicmodule_request(self):
        path = '/logicmodule/'
        response = self.client.get(path)

        # validate result
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.get('content-type'), 'application/json')
        self.assertIsInstance(response.content, bytes)

    def make_logicmodule_request_superuser(self):
        self.core_user.user.is_superuser = True

        path = '/logicmodule/'
        response = self.client.get(path)

        # validate result
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-type'), 'application/json')
        self.assertIsInstance(response.content, bytes)
