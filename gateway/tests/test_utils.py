"""pytest unit tests, to run:
DJANGO_SETTINGS_MODULE=buildly.settings.production pytest gateway/tests/test_utils.py -v --cov
or: pytest -c /dev/null gateway/tests/test_utils.py
"""
import datetime
import json
from unittest.mock import Mock, patch
import uuid

from django.test import TestCase
import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

import factories
from gateway.exceptions import GatewayError
from gateway.utils import (
    GatewayJSONEncoder,
    validate_object_access,
    get_swagger_url_by_logic_module,
    get_swagger_urls,
    get_swagger_from_url,
)
from gateway.views import APIGatewayView


class UtilsValidateBuildlyObjectAccessTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def get_mock_request(self, url, view, user=None):
        request = self.factory.get(url)
        if user is not None:
            request.user = user
            force_authenticate(request, user=user)
        request = view().initialize_request(request)
        return request

    def test_validate_buildly_wfl1_access_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.get_mock_request('/', APIGatewayView, self.core_user)
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        validate_object_access(request, wflvl1)

    def test_validate_buildly_wfl1_no_permission(self):
        request = self.get_mock_request('/', APIGatewayView, self.core_user)
        wflvl1 = factories.WorkflowLevel1()

        error_message = 'You do not have permission to perform this action.'
        with self.assertRaisesMessage(PermissionDenied, error_message):
            validate_object_access(request, wflvl1)

    def test_validate_buildly_wfl1_not_authenticated_user(self):
        request = self.get_mock_request('/', APIGatewayView)
        wflvl1 = factories.WorkflowLevel1()

        error_message = 'Authentication credentials were not provided.'
        with self.assertRaisesMessage(NotAuthenticated, error_message):
            validate_object_access(request, wflvl1)

    def test_validate_buildly_logic_module_no_viewset(self):
        request = self.get_mock_request('/', APIGatewayView, self.core_user)
        lm = factories.LogicModule()

        with self.assertRaises(GatewayError):
            validate_object_access(request, lm)

    def test_validate_core_user_access(self):
        request = self.get_mock_request(
            '/a-jedis-path/', APIGatewayView, self.core_user
        )
        request.resolver_match = Mock(url_name='obi-wan-kenobi')
        core_user = factories.CoreUser()
        ret = validate_object_access(request, core_user)
        self.assertIsNone(ret)


def test_json_dump():
    obj = {
        "string": "test1234",
        "integer": 123,
        "array": ['1', 2],
        "uuid": uuid.UUID('50096bc6-848a-456f-ad36-3ac04607ff67'),
        "datetime": datetime.datetime(2019, 2, 5, 12, 36, 0, 147972),
    }

    response = json.dumps(obj, cls=GatewayJSONEncoder)
    expected_response = (
        '{"string": "test1234",'
        ' "integer": 123,'
        ' "array": ["1", 2],'
        ' "uuid": "50096bc6-848a-456f-ad36-3ac04607ff67",'
        ' "datetime": "2019-02-05T12:36:00.147972"}'
    )
    assert response == expected_response


@pytest.mark.django_db()
def test_json_dump_w_core_user():
    core_user = factories.CoreUser(pk=5)
    obj = {"model_instance": core_user}
    result = json.dumps(obj, cls=GatewayJSONEncoder)
    expected_result = '{"model_instance": 5}'
    assert result == expected_result


def test_json_dump_exception():
    class TestObj(object):
        pass

    test_obj = TestObj()
    error_message = 'Object of type TestObj is not JSON serializable'

    with pytest.raises(TypeError) as exc:
        json.dumps(test_obj, cls=GatewayJSONEncoder)

    assert error_message in str(exc.value)


@pytest.mark.django_db()
class TestGettingSwaggerURLs:
    def test_get_swagger_url_by_logic_module(self):
        module = factories.LogicModule.create()
        url = get_swagger_url_by_logic_module(module)
        assert url.startswith(module.endpoint)

    def test_get_swagger_url_by_logic_module_specified_docs(self):
        module = factories.LogicModule.create(docs_endpoint="api-docs")
        url = get_swagger_url_by_logic_module(module)
        assert url.startswith(module.endpoint)
        assert module.docs_endpoint in url

    def test_get_swagger_urls(self):
        modules = factories.LogicModule.create_batch(3)
        urls = get_swagger_urls()
        for module in modules:
            assert module.endpoint_name in urls
            assert urls[module.endpoint_name] == get_swagger_url_by_logic_module(module)

    @patch('requests.get')
    def test_unavailable_logic_module_timeout_exception(self, mock_request_get):
        mock_request_get.side_effect = TimeoutError
        with pytest.raises(TimeoutError):
            assert get_swagger_from_url('http://example.com')

    @patch('requests.get')
    def test_unavailable_logic_module_connection_exception(self, mock_request_get):
        mock_request_get.side_effect = ConnectionError
        with pytest.raises(ConnectionError):
            assert get_swagger_from_url('http://microservice:5000')
