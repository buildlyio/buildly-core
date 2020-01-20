# TODO: remove, this is for old version of the gateway (_views.py)
import json

import factories

from django.test import TestCase
from rest_framework.test import APIClient

from unittest.mock import Mock, patch
from pyswagger import App
from pyswagger.io import Response as PySwaggerResponse


class APIGatewayViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.core_user = factories.CoreUser()
        self.lm = factories.LogicModule(name='Documents', endpoint_name='documents')

        # bypass authentication
        self.client.force_authenticate(user=self.core_user)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_data_and_raw(self, mock_perform_request, mock_app):
        # expected data
        headers = {'Content-Type': ['application/json']}
        content = b'{"details": "IT IS A TEST"}'

        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = json.loads(content)
        pyswagger_response.raw = content
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/old/{}/{}/1/'.format(self.lm.endpoint_name, 'thumbnail')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.get('Content-Type'), 'application/json')

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_only_raw(self, mock_perform_request, mock_app):
        # expected data
        headers = {'Content-Type': ['text/html; charset=utf-8']}
        content = b'IT IS A TEST'

        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = None
        pyswagger_response.raw = content
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/old/{}/{}/1/'.format(self.lm.endpoint_name, 'thumbnail')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.get('Content-Type'), ''.join(headers.get('Content-Type')))

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_aggregate_only_raw(self, mock_perform_request, mock_app):
        # expected data
        headers = {'Content-Type': ['text/html; charset=utf-8']}
        content = b'IT IS A TEST'

        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = None
        pyswagger_response.raw = content
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/old/{}/{}/1/'.format(self.lm.endpoint_name, 'thumbnail')
        response = self.client.get(path, {'aggregate': 'true'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, content)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.get('Content-Type'), ''.join(headers.get('Content-Type')))

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._get_swagger_data')
    def test_get_req_and_rep_without_pk_raises_exception(self, mock_swagger_data, mock_app):

        mock_swagger_data.return_value = {}

        # mock app
        app = Mock(App)
        app.s.return_value = None
        mock_app.return_value = app

        # make api request
        path = '/old/{}/{}/'.format(self.lm.endpoint_name, 'nowhere')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(json.loads(response.content)['detail'], "Endpoint not found: GET /nowhere/")

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._get_swagger_data')
    def test_get_req_and_rep_with_pk_raises_exception(self, mock_swagger_data, mock_app):
        mock_swagger_data.return_value = {}

        # mock app
        app = Mock(App)
        app.s.side_effect = KeyError()
        mock_app.return_value = app

        # make api request
        path = '/old/{}/{}/123/'.format(self.lm.endpoint_name, 'nowhere')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 404)
        self.assertTrue(response.has_header('Content-Type'))
        self.assertEqual(response.get('Content-Type'), 'application/json')
        self.assertEqual(json.loads(response.content)['detail'], "Endpoint not found: GET /nowhere/{id}/")
