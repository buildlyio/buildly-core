import os
import json

import pytest
import httpretty

from workflow.tests.fixtures import auth_api_client
from .fixtures import logic_module


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_data_and_raw(auth_api_client, logic_module):
    url = f'/{logic_module.endpoint_name}/thumbnail/1/'
    content = '{"details": "IT IS A TEST"}'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger.json')) as r:
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
        adding_headers={'Content-Type': 'application/json'}
    )

    # make api request
    response = auth_api_client.get(url)

    assert response.status_code == 200
    assert response.content == content.encode()
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'application/json'


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_only_raw(auth_api_client, logic_module):

    url = f'/{logic_module.endpoint_name}/thumbnail/1/'
    content = 'IT IS A TEST'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger.json')) as r:
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
        adding_headers={'Content-Type': 'text/html; charset=utf-8'}
    )

    # make api request
    response = auth_api_client.get(url)

    assert response.status_code == 200
    assert response.content == content.encode()
    assert response.has_header('Content-Type')
    assert response.get('Content-Type') == 'text/html; charset=utf-8'


@pytest.mark.django_db()
@httpretty.activate
def test_make_service_request_to_unexisting_list_endpoint(auth_api_client, logic_module):

    url = f'/{logic_module.endpoint_name}/nowhere/'

    # mock requests
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger.json')) as r:
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
    with open(os.path.join(CURRENT_PATH, 'fixtures/swagger.json')) as r:
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
    assert json.loads(response.content)['detail'] == "Endpoint not found: GET /nowhere/{id}/"
