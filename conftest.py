import pytest
from rest_framework.test import APIRequestFactory


@pytest.fixture(scope='session')
def req_factory():
    return APIRequestFactory()
