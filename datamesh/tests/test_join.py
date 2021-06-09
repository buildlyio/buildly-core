import json
from unittest.mock import Mock, patch

import pytest
from bravado_core.spec import Spec

import factories
from datamesh.tests.fixtures import relationship, relationship2, relationship_with_10_records
from core.tests.fixtures import auth_api_client, org

@pytest.mark.django_db()
@patch('gateway.request.GatewayRequest._get_swagger_spec')
@patch('gateway.request.SwaggerClient.request')
def test_join_data_one_obj_w_relationships(mock_perform_request, mock_spec, auth_api_client, relationship):
    factories.JoinRecord(relationship=relationship, record_id=1, related_record_id=2,
                         record_uuid=None, related_record_uuid=None)
    # mock app
    mock_spec.return_value = Mock(Spec)

    # mock first response
    service_response = ({'id': 1, 'name': 'test', 'contact_uuid': 1},
                        200, {'Content-Type': ['application/json']})
    # mock second response
    expand_response = ({'id': 1, 'file': '/somewhere/128/',},
                       200, {'Content-Type': ['application/json']})
    mock_perform_request.side_effect = [service_response, expand_response]

    # make api request
    path = '/{}/{}/'.format(relationship.origin_model.logic_module_endpoint_name, 'products')
    response = auth_api_client.get(path, {'join': ''})

    # validate result
    expected_data = {
        'id': 1,
        'name': 'test',
        'contact_uuid': 1,
        relationship.key: [{
            'id': 1,
            'file': '/somewhere/128/',
        }]
    }

    assert response.status_code == 200
    assert json.loads(response.content) == expected_data


@pytest.mark.django_db()
@patch('gateway.request.GatewayRequest._get_swagger_spec')
@patch('gateway.request.SwaggerClient.request')
def test_join_data_one_obj_w_two_relationships(mock_perform_request, mock_spec, auth_api_client,
                                               relationship, relationship2):
    factories.JoinRecord(relationship=relationship, record_id=1, related_record_id=2,
                         record_uuid=None, related_record_uuid=None)
    factories.JoinRecord(relationship=relationship2, record_id=1, related_record_id=10,
                         record_uuid=None, related_record_uuid=None)

    mock_spec.return_value = Mock(Spec)
    # mock first response
    service_response = ({'id': 1, 'name': 'test', 'contact_uuid': 1},
                        200, {'Content-Type': ['application/json']})
    # mock second response
    expand_response1 = ({'id': 2, 'file': '/documents/128/'},
                        200, {'Content-Type': ['application/json']})
    # mock third response
    expand_response2 = ({'id': 10, 'city': 'New York'},
                        200, {'Content-Type': ['application/json']})
    mock_perform_request.side_effect = [service_response, expand_response1, expand_response2]

    # make api request
    path = '/{}/{}/'.format(relationship.origin_model.logic_module_endpoint_name, 'products')
    response = auth_api_client.get(path, {'join': ''})

    # validate result
    expected_data = {
        'id': 1,
        'name': 'test',
        'contact_uuid': 1,
        relationship.key: [{
            'id': 2,
            'file': '/documents/128/',
        }],
        relationship2.key: [{
            'id': 10,
            'city': 'New York',
        }]
    }

    assert response.status_code == 200
    assert json.loads(response.content) == expected_data


@pytest.mark.django_db()
@patch('gateway.request.GatewayRequest._get_swagger_spec')
@patch('gateway.request.SwaggerClient.request')
def test_join_data_list(mock_perform_request, mock_spec, auth_api_client, relationship_with_10_records, org):
    mock_spec.return_value = Mock(Spec)

    join_records = relationship_with_10_records.joinrecords.all()
    main_service_data = [{'uuid': item.record_uuid, 'name': f'Boiler #{i}'}
                         for i, item in enumerate(join_records)]
    main_service_response = (main_service_data,
                             200, {'Content-Type': ['application/json']})

    expand_responses = []
    for item in join_records:
        expand_responses.append(
            ({'uuid': item.related_record_uuid, 'file': '/documents/128/'},
             200, {'Content-Type': ['application/json']})
        )
    mock_perform_request.side_effect = [main_service_response] + expand_responses

    # make api request
    path = '/{}/{}/'.format(relationship_with_10_records.origin_model.logic_module_endpoint_name, 'products')
    response = auth_api_client.get(path, {'join': ''})

    assert response.status_code == 200
    for i, item in enumerate(json.loads(response.content)):
        assert item['uuid'] == str(join_records[i].record_uuid)
        assert relationship_with_10_records.key in item
        nested = item[relationship_with_10_records.key]
        assert len(nested) == 1
        assert nested[0]['uuid'] == str(join_records[i].related_record_uuid)
