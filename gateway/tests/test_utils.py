"""pytest unit tests, to run:
DJANGO_SETTINGS_MODULE=bifrost-api.settings.production py.test gateway/tests/test_utils.py -v --cov
or: pytest gateway/tests/test_utils.py
"""
import uuid
import datetime
import pytest

import factories

from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.exceptions import NotAuthenticated, PermissionDenied

from gateway.exceptions import GatewayError
from gateway.views import APIGatewayView
from gateway.utils import json_dump, validate_object_access


class UtilsValidateBifrostObjectAccessTest(TestCase):
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

    def test_validate_bifrost_wfl1_access_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.get_mock_request('/', APIGatewayView,
                                        self.core_user.user)
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        validate_object_access(request, wflvl1)

    def test_validate_bifrost_wfl1_no_permission(self):
        request = self.get_mock_request('/', APIGatewayView,
                                        self.core_user.user)
        wflvl1 = factories.WorkflowLevel1()

        error_message = 'You do not have permission to perform this action.'
        with self.assertRaisesMessage(PermissionDenied, error_message):
            validate_object_access(request, wflvl1)

    def test_validate_bifrost_wfl1_not_authenticated_user(self):
        request = self.get_mock_request('/', APIGatewayView)
        wflvl1 = factories.WorkflowLevel1()

        error_message = 'Authentication credentials were not provided.'
        with self.assertRaisesMessage(NotAuthenticated, error_message):
            validate_object_access(request, wflvl1)

    def test_validate_bifrost_logic_module_no_viewset(self):
        request = self.get_mock_request('/', APIGatewayView,
                                        self.core_user.user)
        lm = factories.LogicModule()

        with self.assertRaises(GatewayError):
            validate_object_access(request, lm)


def test_json_dump():
    obj = {
        "string": "test1234",
        "integer": 123,
        "array": ['1', 2, ],
        "uuid": uuid.UUID('50096bc6-848a-456f-ad36-3ac04607ff67'),
        "datetime": datetime.datetime(2019, 2, 5, 12, 36, 0, 147972)
    }
    response = json_dump(obj)
    expected_response = '{"string": "test1234",' \
                        ' "integer": 123,' \
                        ' "array": ["1", 2],' \
                        ' "uuid": "50096bc6-848a-456f-ad36-3ac04607ff67",' \
                        ' "datetime": "2019-02-05T12:36:00.147972"}'
    assert response == expected_response


def test_json_dump_exception():

    class TestObj(object):
        pass

    test_obj = TestObj()

    with pytest.raises(TypeError) as exc:
        json_dump(test_obj)

    assert 'is not handled' in str(exc.value)
