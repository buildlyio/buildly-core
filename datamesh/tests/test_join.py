import json
from unittest.mock import Mock, patch

import pytest
from pyswagger import App
from pyswagger.io import Response as PySwaggerResponse

import factories
from datamesh.tests.fixtures import relationship
from workflow.tests.fixtures import auth_api_client


@pytest.mark.django_db()
class TestDataMesh:

    @patch('gateway.views.APIGatewayView._load_swagger_resource')
    @patch('gateway.views.APIGatewayView._perform_service_request')
    def test_join_data_one_obj_w_relationships(self, mock_perform_request, mock_app, auth_api_client, relationship):
        factories.JoinRecord(relationship=relationship, record_id=1, related_record_id=2)
        # mock app
        mock_app.return_value = Mock(App)

        # mock first response
        headers = {'Content-Type': ['application/json']}
        service_response = Mock(PySwaggerResponse)
        service_response.status = 200
        service_response.data = {
            'id': 1,
            'name': 'test',
            'contact_uuid': 1
        }
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
        path = '/{}/{}/'.format(relationship.origin_model.logic_module.endpoint_name, 'products')
        response = auth_api_client.get(path, {'join': ''})

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

        assert response.status_code == 200
        assert json.loads(response.content) == expected_data
