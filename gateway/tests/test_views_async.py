import os
import json
from unittest.mock import patch

import pytest

import factories
from core.tests.fixtures import auth_api_client, logic_module
from .fixtures import datamesh
from .utils import AiohttpResponseMock, create_aiohttp_session_mock


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("content,content_type", [
    (b'{"details": "IT IS A TEST"}', 'application/json'),
    (b'IT IS A TEST', 'text/html; charset=utf-8'),
    (None, 'application/octet-stream'), ]
)
@pytest.mark.django_db()
@patch('gateway.request.aiohttp.ClientSession')
def test_make_service_request_data_and_raw(client_session_mock, auth_api_client, logic_module, content, content_type,
                                           event_loop):
    url = f'/async/{logic_module.endpoint_name}/thumbnail/1/'

    # mock aiohttp responses
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json'), 'rb') as r:
        swagger_body = r.read()

    responses = [
        AiohttpResponseMock(method='GET', url=f'{logic_module.endpoint}/docs/swagger.json', status=200,
                            body=swagger_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{logic_module.endpoint}/thumbnail/1/', status=200, body=content,
                            headers={'Content-Type': content_type}),
    ]
    client_session_mock.return_value = create_aiohttp_session_mock(responses, loop=event_loop)

    # make api request
    response = auth_api_client.get(url)

    assert response.status_code == 200
    if content:
        assert response.content == content
    else:
        assert response.content == b''
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == content_type


@pytest.mark.django_db()
@patch('gateway.request.aiohttp.ClientSession')
def test_make_service_request_to_unexisting_list_endpoint(client_session_mock, auth_api_client, logic_module,
                                                          event_loop):

    url = f'/async/{logic_module.endpoint_name}/nowhere/'

    # mock aiohttp responses
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json'), 'rb') as r:
        swagger_body = r.read()
    responses = [
        AiohttpResponseMock(method='GET', url=f'{logic_module.endpoint}/docs/swagger.json', status=200,
                            body=swagger_body, headers={'Content-Type': 'application/json'}),
    ]
    client_session_mock.return_value = create_aiohttp_session_mock(responses, loop=event_loop)

    # make api request
    response = auth_api_client.get(url)

    # This operation doesn't exist in Swagger schema so 404 must be thrown
    assert response.status_code == 404
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    assert json.loads(response.content)['detail'] == "Endpoint not found: GET /nowhere/"


@pytest.mark.django_db()
@patch('gateway.request.aiohttp.ClientSession')
def test_make_service_request_to_unexisting_detail_endpoint(client_session_mock, auth_api_client, logic_module,
                                                            event_loop):

    url = f'/async/{logic_module.endpoint_name}/nowhere/123/'

    # mock aiohttp responses
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json'), 'rb') as r:
        swagger_body = r.read()
    responses = [
        AiohttpResponseMock(method='GET', url=f'{logic_module.endpoint}/docs/swagger.json', status=200,
                            body=swagger_body, headers={'Content-Type': 'application/json'}),
    ]
    client_session_mock.return_value = create_aiohttp_session_mock(responses, loop=event_loop)

    # make api request
    response = auth_api_client.get(url)

    # This operation doesn't exist in Swagger schema so 404 must be thrown
    assert response.status_code == 404
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    assert json.loads(response.content)['detail'] == "Endpoint not found: GET /nowhere/{nowhere_id}/"


@pytest.mark.django_db()
@patch('gateway.request.aiohttp.ClientSession')
def test_make_service_request_with_datamesh_detailed(client_session_mock, auth_api_client, datamesh, event_loop):
    lm1, lm2, relationship = datamesh
    factories.JoinRecord(relationship=relationship,
                         record_id=None, record_uuid='19a7f600-74a0-4123-9be5-dfa69aa172cc',
                         related_record_id=1, related_record_uuid=None)

    url = f'/async/{lm1.endpoint_name}/siteprofiles/19a7f600-74a0-4123-9be5-dfa69aa172cc/'

    # mock aiohttp responses
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_location.json'), 'rb') as r:
        swagger_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json'), 'rb') as r:
        swagger_documents_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_siteprofile.json'), 'rb') as r:
        data_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_document.json'), 'rb') as r:
        data_documents_body = r.read()
    responses = [
        AiohttpResponseMock(method='GET', url=f'{lm1.endpoint}/docs/swagger.json', status=200,
                            body=swagger_location_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm2.endpoint}/docs/swagger.json', status=200,
                            body=swagger_documents_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm1.endpoint}/siteprofiles/19a7f600-74a0-4123-9be5-dfa69aa172cc/',
                            status=200,
                            body=data_location_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm2.endpoint}/documents/1/', status=200,
                            body=data_documents_body, headers={'Content-Type': 'application/json'}),
    ]
    client_session_mock.return_value = create_aiohttp_session_mock(responses, loop=event_loop)

    # make api request
    response = auth_api_client.get(url, {'join': 'true'})

    assert response.status_code == 200
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    data = response.json()
    assert relationship.key in data
    assert len(data[relationship.key]) == 1
    assert data[relationship.key][0][list(data[relationship.key][0].keys())[0]] == 1


@pytest.mark.django_db()
@patch('gateway.request.aiohttp.ClientSession')
def test_make_service_request_with_datamesh_list(client_session_mock, auth_api_client, datamesh, event_loop):
    lm1, lm2, relationship = datamesh
    factories.JoinRecord(relationship=relationship,
                         record_id=None, record_uuid='19a7f600-74a0-4123-9be5-dfa69aa172cc',
                         related_record_id=1, related_record_uuid=None)

    url = f'/async/{lm1.endpoint_name}/siteprofiles/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_location.json'), 'rb') as r:
        swagger_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json'), 'rb') as r:
        swagger_documents_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_list_siteprofile.json'), 'rb') as r:
        data_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_document.json'), 'rb') as r:
        data_documents_body = r.read()
    responses = [
        AiohttpResponseMock(method='GET', url=f'{lm1.endpoint}/docs/swagger.json', status=200,
                            body=swagger_location_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm2.endpoint}/docs/swagger.json', status=200,
                            body=swagger_documents_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm1.endpoint}/siteprofiles/', status=200,
                            body=data_location_body, headers={'Content-Type': 'application/json'}),
        AiohttpResponseMock(method='GET', url=f'{lm2.endpoint}/documents/1/', status=200,
                            body=data_documents_body, headers={'Content-Type': 'application/json'}),
    ]
    client_session_mock.return_value = create_aiohttp_session_mock(responses, loop=event_loop)

    # make api request
    response = auth_api_client.get(url, {'join': 'true'})

    assert response.status_code == 200
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    data = response.json()

    # first item in the list has a joined record
    item1 = data["results"][0]
    assert relationship.key in item1
    assert len(item1[relationship.key]) == 1
    assert item1[relationship.key][0][list(item1[relationship.key][0].keys())[0]] == 1

    # second item in the list doesn't have a joined record
    item2 = data["results"][1]
    assert relationship.key in item2
    assert len(item2[relationship.key]) == 0
