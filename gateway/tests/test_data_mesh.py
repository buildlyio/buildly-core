import factories
import json
from urllib import error

from django.test import TestCase
from django.forms.models import model_to_dict
from rest_framework.test import APIClient

from unittest.mock import Mock, patch
from pyswagger import App
from pyswagger.io import Response as PySwaggerResponse

from gateway import exceptions, utils


class DataMeshTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.core_user = factories.CoreUser()
        self.lm = factories.LogicModule(name='products')

        # bypass authentication
        self.client.force_authenticate(user=self.core_user.user)
        self.response_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': 1
        }

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_content(self, mock_perform_request,
                                          mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'example')
        response = self.client.get(path)

        # validate result
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('content-type'), 'application/json')
        self.assertIsInstance(response.content, bytes)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    def test_make_service_request_content_raises_exception(
            self, mock_perform_request):
        # mock response
        msg = 'Service "{}" not found.'.format(self.lm.name)
        exception_obj = exceptions.ServiceDoesNotExist(msg=msg, status=404)
        mock_perform_request.side_effect = exception_obj

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'example')
        response = self.client.get(path)

        # validate result
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get('content-type'), 'application/json')
        self.assertEqual(json.loads(response.content), {'detail': msg})

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._aggregate_response_data')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_aggregate_content(
            self, mock_perform_request, mock_aggregate_response_data,
            mock_app):
        response_data = {
            'id': 1,
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            },
            'name': 'test',
            'contact_uuid': 1
        }

        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'example')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.content, bytes)

    @patch('gateway.views.logger')
    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._aggregate_response_data')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_make_service_request_aggregate_raises_exception(
            self, mock_perform_request, mock_aggregate_response_data,
            mock_app, mock_logger):
        # mock app
        mock_app.return_value = Mock(App)

        # mock aggregate response data
        msg = 'Service "{}" not found.'.format(self.lm.name)
        exception_obj = exceptions.ServiceDoesNotExist(msg=msg)
        mock_aggregate_response_data.side_effect = exception_obj

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'example')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.content, bytes)
        mock_logger.error.assert_called_with(json.dumps({'detail': msg}))

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._expand_data')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_aggregate_data_one_obj(self, mock_perform_request,
                                    mock_expand_data, mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # mock expand data
        external_data = {
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            }
        }
        mock_expand_data.return_value = external_data

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            },
            'name': 'test',
            'contact_uuid': 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._expand_data')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_aggregate_data_list_of_objs(self, mock_perform_request,
                                         mock_expand_data, mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = [self.response_data]
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # mock expand data
        external_data = {
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            }
        }
        mock_expand_data.return_value = external_data

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = [{
            'id': 1,
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            },
            'name': 'test',
            'contact_uuid': 1
        }]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._expand_data')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_aggregate_data_dict_list_of_objs(self, mock_perform_request,
                                              mock_expand_data, mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = {'results': [self.response_data]}
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # mock expand data
        external_data = {
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            }
        }
        mock_expand_data.return_value = external_data

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {'results': [{
            'id': 1,
            'workflowlevel2_uuid': {
                'id': 1,
                'workflowlevel1': 1,
            },
            'name': 'test',
            'contact_uuid': 1
        }]}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('gateway.views.logger')
    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    @patch('gateway.views.gtm.LogicModule.objects.get')
    def test_aggregate_data_raises_exception(
            self, mock_logic_module_get, mock_perform_request,
            mock_app, mock_logger):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # mock logic module get
        msg = 'Service "{}" not found.'.format(self.lm.name)
        exception_obj = exceptions.ServiceDoesNotExist(msg=msg)
        mock_logic_module_get.side_effect = exception_obj

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        self.assertEqual(response.status_code, 200)
        mock_logger.error.assert_called_with(json.dumps({'detail': msg}))

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_expand_data_from_bifrost_superuser(self, mock_perform_request,
                                           mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # create expand data
        wfl2 = factories.WorkflowLevel2()
        self.response_data['workflowlevel2_uuid'] = wfl2.id

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        self.core_user.user.is_superuser = True

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': model_to_dict(wfl2),
            'name': 'test',
            'contact_uuid': 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('utf-8'),
                         json.dumps(expected_data,
                                    cls=utils.GatewayJSONEncoder))

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_expand_data_from_bifrost_permission_denied(self,
                                                        mock_perform_request,
                                                        mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # create expand data
        wfl2 = factories.WorkflowLevel2()

        self.response_data['workflowlevel2_uuid'] = wfl2.id

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')

        # first without permissions
        expected_message = 'You do not have permission to perform this action.'

        response = self.client.get(path, {'aggregate': 'true'})

        self.assertEqual(response.status_code, 403)
        self.assertEqual(json.loads(response.content)['detail'],
                         expected_message)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_expand_data_from_external_service(self, mock_perform_request,
                                               mock_app):
        # update relationships
        self.lm.relationships['products'] = {
            'contact_uuid': 'crm.Contact'
        }
        self.lm.save()

        # mock app
        mock_app.return_value = Mock(App)

        # mock service response
        headers = {'Content-Type': ['application/json']}
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = self.response_data
        service_response.header = headers

        # mock expand response
        expand_data = {
            'first_name': 'Jeferson',
            'last_name': 'Moura',
            'contact_type': 'company',
            'company': 'Humanitec'
        }
        expand_response = Mock(PySwaggerResponse)
        expand_response.data = expand_data
        mock_perform_request.side_effect = [service_response, expand_response]

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': expand_data
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_expand_data_from_bifrost_raises_exception(
            self, mock_perform_request, mock_app):
        # mock app
        mock_app.return_value = Mock(App)

        # mock response
        headers = {'Content-Type': ['application/json']}
        pyswagger_response = Mock(PySwaggerResponse)
        pyswagger_response.status = 200
        pyswagger_response.data = self.response_data
        pyswagger_response.header = headers
        mock_perform_request.return_value = pyswagger_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('pyswagger.App.load')
    @patch('gateway.utils')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_load_swagger_resource_of_external_service(
            self, mock_perform_request, mock_utils, mock_app):
        # create extra service
        crm_lm = factories.LogicModule(
            name='crm',
            endpoint='http://crm.example.com',
            relationships={}
        )

        # update relationships
        self.lm.relationships['products'] = {
            'contact_uuid': 'crm.Contact'
        }
        self.lm.save()

        # mock schema urls and app
        product_schema_url = {
            self.lm.name: self.lm.endpoint
        }
        crm_schema_url = {
            'crm': crm_lm.endpoint
        }
        mock_utils.get_swagger_urls.side_effect = [product_schema_url,
                                                   crm_schema_url]
        mock_app.return_value = Mock(App)

        # mock service response
        headers = {'Content-Type': ['application/json']}
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = self.response_data
        service_response.header = headers

        # mock expand response
        expand_data = {
            'first_name': 'Jeferson',
            'last_name': 'Moura',
            'contact_type': 'company',
            'company': 'Humanitec'
        }
        expand_response = Mock(PySwaggerResponse)
        expand_response.data = expand_data
        mock_perform_request.side_effect = [service_response, expand_response]

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': expand_data
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('pyswagger.App.load')
    @patch('gateway.utils')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_load_swagger_resource_aggregate_raises_exception(
            self, mock_perform_request, mock_utils, mock_app):
        # mock schema urls and app
        product_schema_url = {
            self.lm.name: self.lm.endpoint
        }
        msg = 'Service "crm" not found.'
        exception_obj = exceptions.ServiceDoesNotExist(msg=msg)
        mock_utils.get_swagger_urls.side_effect = [product_schema_url,
                                                   exception_obj]
        mock_app.return_value = Mock(App)

        # mock service response
        headers = {'Content-Type': ['application/json']}
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = self.response_data
        service_response.header = headers
        mock_perform_request.return_value = service_response

        # make api request
        path = '/{}/{}/'.format(self.lm.name, 'products')
        response = self.client.get(path, {'aggregate': 'true'})

        # validate result
        expected_data = {
            'id': 1,
            'workflowlevel2_uuid': 1,
            'name': 'test',
            'contact_uuid': 1
        }
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)

    @patch('pyswagger.App.load')
    @patch('gateway.utils')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_load_swagger_resource_aggregate_raises_url_error(
            self, mock_perform_request, mock_utils, mock_app):
        # create extra service
        crm_lm = factories.LogicModule(
            name='crm',
            endpoint='http://crm.example.com',
            relationships={}
        )

        # mock schema urls and app
        product_schema_url = {
            self.lm.name: self.lm.endpoint
        }
        crm_schema_url = {
            'crm': crm_lm.endpoint
        }
        mock_utils.get_swagger_urls.side_effect = [product_schema_url,
                                                   crm_schema_url]
        msg = f'Make sure that {crm_lm.endpoint} is accessible.'
        exception_obj = error.URLError(msg)
        mock_app.side_effect = exception_obj

        # mock service response
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = self.response_data
        mock_perform_request.return_value = service_response

        # make api request and validate error
        path = '/{}/{}/'.format(self.lm.name, 'products')
        with self.assertRaises(error.URLError) as context:
            self.client.get(path, {'aggregate': 'true'})
            self.assertTrue(msg in context.exception)
