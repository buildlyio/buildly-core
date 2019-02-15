import pytest

from django.conf import settings

from oauthlib.oauth2 import BearerToken

import factories

from .. import utils

# ------------ Fixtures ------------------


@pytest.fixture
def org():
    return factories.Organization()


@pytest.fixture
def core_user(org):
    return factories.CoreUser.create(organization=org)


@pytest.fixture
def application(org):
    return factories.Application.create(
        client_id=settings.SOCIAL_AUTH_CLIENT_ID,
        client_secret=settings.SOCIAL_AUTH_CLIENT_SECRET
    )

# ------------ Tests ------------------


class TestGenerateTokens(object):

    @pytest.mark.django_db()
    def test_success(self, wsgi_request_factory, core_user,
                                      application, monkeypatch):

        def mock_create_token(*args, **kwargs):
            return token

        def mock_generate_payload(*args, **kwargs):
            return {
                'iss': 'BifrostTest',
                'exp': 36000,
                'iat': 'testing',
            }

        def mock_encode_jwt(*args, **kwargs):
            return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'

        final_token = {
            'access_token': 'bZr9TVYykJnbVL1gAjq4Xhn3x1SY91',
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': 'UDJsQxZpjVxhuOgrCMLHnc79NI5ZpU',
            'access_token_jwt': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9'
        }

        token = {
            'access_token': 'bZr9TVYykJnbVL1gAjq4Xhn3x1SY91',
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': 'UDJsQxZpjVxhuOgrCMLHnc79NI5ZpU',
        }

        # remove jwt enricher
        monkeypatch.delattr('django.conf.settings.JWT_PAYLOAD_ENRICHER')

        # mock functions in order as in the code
        monkeypatch.setattr(BearerToken, 'create_token', mock_create_token)
        monkeypatch.setattr(utils, 'generate_payload', mock_generate_payload)
        monkeypatch.setattr(utils, 'encode_jwt', mock_encode_jwt)

        # mock request object
        request = wsgi_request_factory()

        result = utils.generate_access_tokens(request, core_user.user)
        assert result == final_token

    @pytest.mark.django_db()
    def test_without_encode_mock_success(self, wsgi_request_factory, core_user,
                     application, monkeypatch):
        def mock_create_token(*args, **kwargs):
            return token

        def mock_generate_payload(*args, **kwargs):
            return {
                'iss': 'bifrost',
                'exp': 36000,
                'iat': 'testing',
            }

        token = {
            'access_token': 'bZr9TVYykJnbVL1gAjq4Xhn3x1SY91',
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': 'UDJsQxZpjVxhuOgrCMLHnc79NI5ZpU',
        }

        # remove jwt enricher
        monkeypatch.delattr('django.conf.settings.JWT_PAYLOAD_ENRICHER')

        # mock functions in order as in the code
        monkeypatch.setattr(BearerToken, 'create_token', mock_create_token)
        monkeypatch.setattr(utils, 'generate_payload', mock_generate_payload)

        # mock request object
        request = wsgi_request_factory()

        # the tokens change all the time, it's not possible to validate them
        # just check if the function doesn't raise an error when providing
        # all needed parameters
        utils.generate_access_tokens(request, core_user.user)

    @pytest.mark.django_db()
    def test_no_func_mocks_success(self, wsgi_request_factory, core_user,
                                   application, monkeypatch):
        # remove jwt enricher
        monkeypatch.delattr('django.conf.settings.JWT_PAYLOAD_ENRICHER')

        # mock request object
        request = wsgi_request_factory()

        # the tokens change all the time, it's not possible to validate them
        # just check if the function doesn't raise an error when providing
        # all needed parameters
        utils.generate_access_tokens(request, core_user.user)
