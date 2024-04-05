import pytest

from django.core.handlers.wsgi import WSGIRequest
from rest_framework.test import APIRequestFactory


@pytest.fixture(scope='session')
def request_factory():
    return APIRequestFactory()


@pytest.fixture(scope='session')
def wsgi_request_factory():
    def _make_wsgi_request(data: dict = None):
        environ = {
            'REQUEST_METHOD': 'get',
            'SERVER_NAME': 'localhost',
            'SERVER_PORT': 8080,
            'wsgi.input': '',
        }
        if data:
            environ.update(data)

        return WSGIRequest(environ)

    return _make_wsgi_request
