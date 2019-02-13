import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture(scope='session')
def request_factory():
    return APIRequestFactory()
