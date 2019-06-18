import uuid

import factories
import json

from django.test import TestCase
from rest_framework.test import APIClient

from unittest.mock import Mock, patch
from pyswagger import App
from pyswagger.io import Response as PySwaggerResponse


class DataMeshTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.core_user = factories.CoreUser()
        self.lm = factories.LogicModule(name='Products Service', endpoint_name='products')
        self.lm_document = factories.LogicModule(name='Document Service', endpoint_name='documents')
        self.lmm = factories.LogicModuleModel(logic_module=self.lm, model='Product', endpoint='/products/')
        self.lmm_document = factories.LogicModuleModel(logic_module=self.lm_document, model='Document', endpoint='/documents/')
        self.relationship = factories.Relationship(origin_model=self.lmm, related_model=self.lmm_document, key='document_relationship')

        # bypass authentication
        self.client.force_authenticate(user=self.core_user)
        self.response_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1
        }

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_join_data_one_obj_w_relationships(self,
                                               mock_perform_request,
                                               mock_app):
        factories.JoinRecord(relationship=self.relationship,
                             record_id=1,
                             related_record_id=2)
        # mock app
        mock_app.return_value = Mock(App)

        # mock first response
        headers = {'Content-Type': ['application/json']}
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = self.response_data
        service_response.header = headers
        # mock second response
        expand_data = {
            'id': 1,
            'file': '/somewhere/128/',
        }
        expand_response = Mock(PySwaggerResponse)
        expand_response.data = expand_data
        mock_perform_request.side_effect = [service_response, expand_response]

        # make api request
        path = '/{}/{}/'.format(self.lm.endpoint_name, 'products')
        response = self.client.get(path, {'join': ''})

        # validate result
        expected_data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1,
            'document_relationship': [{
                'id': 1,
                'file': '/somewhere/128/',
            }]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), expected_data)
