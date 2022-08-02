import os
import json

import pytest
import httpretty

import factories
from core.tests.fixtures import auth_api_client, logic_module
from datamesh.models import LogicModuleModel
from .fixtures import datamesh


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.parametrize("content,content_type", [('{"details": "IT IS A TEST"}', 'application/json'),
                                                  ('IT IS A TEST', 'text/html; charset=utf-8')])
@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_data_and_raw(auth_api_client, logic_module, content, content_type):
    url = f'/{logic_module.endpoint_name}/thumbnail/1/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{logic_module.endpoint}/docs/swagger.json',
        body=swagger_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{logic_module.endpoint}/thumbnail/1/',
        body=content,
        adding_headers={'Content-Type': content_type}
    )

    # make api request
    response = auth_api_client.get(url)

    assert response.status_code == 200
    assert response.content == content.encode()
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == content_type


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_to_unexisting_list_endpoint(auth_api_client, logic_module):

    url = f'/{logic_module.endpoint_name}/nowhere/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{logic_module.endpoint}/docs/swagger.json',
        body=swagger_body,
        adding_headers={'Content-Type': 'application/json'}
    )

    # make api request
    response = auth_api_client.get(url)

    # This operation doesn't exist in Swagger schema so 404 must be thrown
    assert response.status_code == 404
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    assert json.loads(response.content)['detail'] == "Endpoint not found: GET /nowhere/"


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_to_unexisting_detail_endpoint(auth_api_client, logic_module):

    url = f'/{logic_module.endpoint_name}/nowhere/123/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{logic_module.endpoint}/docs/swagger.json',
        body=swagger_body,
        adding_headers={'Content-Type': 'application/json'}
    )

    # make api request
    response = auth_api_client.get(url)

    # This operation doesn't exist in Swagger schema so 404 must be thrown
    assert response.status_code == 404
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    assert json.loads(response.content)['detail'] == "Endpoint not found: GET /nowhere/{nowhere_id}/"


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_with_datamesh_detailed(auth_api_client, datamesh):
    lm1, lm2, relationship = datamesh
    factories.JoinRecord(relationship=relationship,
                         record_id=None, record_uuid='19a7f600-74a0-4123-9be5-dfa69aa172cc',
                         related_record_id=1, related_record_uuid=None)

    url = f'/{lm1.endpoint_name}/siteprofiles/19a7f600-74a0-4123-9be5-dfa69aa172cc/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_location.json')) as r:
        swagger_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_documents_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_siteprofile.json')) as r:
        data_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_document.json')) as r:
        data_documents_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/docs/swagger.json',
        body=swagger_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/docs/swagger.json',
        body=swagger_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/siteprofiles/19a7f600-74a0-4123-9be5-dfa69aa172cc/',
        body=data_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/documents/1/',
        body=data_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )

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
@httpretty.activate
def test_make_service_request_with_reverse_datamesh_detailed(auth_api_client, datamesh):
    lm1, lm2, relationship = datamesh

    factories.JoinRecord(relationship=relationship,
                         record_id=None, record_uuid='19a7f600-74a0-4123-9be5-dfa69aa172cc',
                         related_record_id=1, related_record_uuid=None)

    url = f'/{lm2.endpoint_name}/documents/1/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_location.json')) as r:
        swagger_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_documents_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_siteprofile.json')) as r:
        data_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_document.json')) as r:
        data_documents_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/docs/swagger.json',
        body=swagger_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/docs/swagger.json',
        body=swagger_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/siteprofiles/19a7f600-74a0-4123-9be5-dfa69aa172cc/',
        body=data_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/documents/1/',
        body=data_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )

    # make api request
    response = auth_api_client.get(url, {'join': 'true'})

    assert response.status_code == 200
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'
    data = response.json()
    assert relationship.key in data
    assert len(data[relationship.key]) == 1
    assert data[relationship.key][0][list(data[relationship.key][0].keys())[0]] == '19a7f600-74a0-4123-9be5-dfa69aa172cc'


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_with_datamesh_list(auth_api_client, datamesh):
    lm1, lm2, relationship = datamesh
    factories.JoinRecord(relationship=relationship,
                         record_id=None, record_uuid='19a7f600-74a0-4123-9be5-dfa69aa172cc',
                         related_record_id=1, related_record_uuid=None)

    url = f'/{lm1.endpoint_name}/siteprofiles/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_location.json')) as r:
        swagger_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger_documents.json')) as r:
        swagger_documents_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_list_siteprofile.json')) as r:
        data_location_body = r.read()
    with open(os.path.join(CURRENT_PATH, 'fixtures/data_detail_document.json')) as r:
        data_documents_body = r.read()
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/docs/swagger.json',
        body=swagger_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/docs/swagger.json',
        body=swagger_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm1.endpoint}/siteprofiles/',
        body=data_location_body,
        adding_headers={'Content-Type': 'application/json'}
    )
    httpretty.register_uri(
        httpretty.GET,
        f'{lm2.endpoint}/documents/1/',
        body=data_documents_body,
        adding_headers={'Content-Type': 'application/json'}
    )

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
