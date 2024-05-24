import pytest
import factories

from unittest.mock import Mock

from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from core.views.logicmodule import LogicModuleViewSet
from core.tests.fixtures import logic_module, superuser
from gateway import utils


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
            'contact_uuid': 1,
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


@pytest.mark.django_db()
class TestLogicModuleUpdate:
    def test_logic_module_update_api_specification(
        self, request_factory, superuser, logic_module, monkeypatch
    ):
        mocked_url = Mock(return_value='example.com')
        test_swagger = {'name': 'example'}
        mocked_swagger = Mock()
        mocked_swagger.return_value.json.return_value = test_swagger

        monkeypatch.setattr(utils, 'get_swagger_url_by_logic_module', mocked_url)
        monkeypatch.setattr(utils, 'get_swagger_from_url', mocked_swagger)

        request = request_factory.put(
            reverse('logicmodule-update-api-specification', args=(logic_module.pk,))
        )
        request.user = superuser
        view = LogicModuleViewSet.as_view({'put': 'update_api_specification'})
        response = view(request, pk=logic_module.pk)
        assert response.status_code == 200

        logic_module.refresh_from_db()
        assert logic_module.api_specification == test_swagger
