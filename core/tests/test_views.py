import pytest
import json

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test import Client, RequestFactory, TestCase

from rest_framework.reverse import reverse

from social_core.backends import oauth
from social_core.exceptions import AuthFailed

from unittest.mock import Mock

import factories

from ..views import web
from ..exceptions import SocialAuthFailed, SocialAuthNotConfigured

# ------------ Fixtures ------------------


@pytest.fixture
def org():
    return factories.Organization()


@pytest.fixture
def core_user(org):
    return factories.CoreUser.create(organization=org)


# ------------ Tests ------------------


class IndexViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_dispatch_unauthenticated(self):
        request = self.factory.get('', follow=True)
        request.user = AnonymousUser()
        response = web.IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)
        template_content = str(response.render().content)
        docs_url = reverse('schema-swagger-ui')
        self.assertIn(f'href="{docs_url}"', template_content)


class HealthCheckViewTest(TestCase):
    def test_health_check_success(self):
        c = Client()
        response = c.get('/health_check/')
        self.assertEqual(response.status_code, 200)


class TestOAuthComplete(object):
    def test_no_code_fail(self, client):
        oauth_url = reverse('oauth_complete', args=('github',))
        expected_data = {'detail': 'Authorization code has to be provided.'}

        response = client.get(oauth_url)

        data = json.loads(response.content)
        assert response.status_code == 400
        assert data == expected_data

    @pytest.mark.django_db()
    def test_is_authenticated_success(
        self, wsgi_request_factory, core_user, monkeypatch
    ):
        def mock_auth_complete(*args, **kwargs):
            return core_user

        tokens = {
            'access_token': 'bZr9TVYykJnbVL1gAjq4Xhn3x1SY91',
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': 'UDJsQxZpjVxhuOgrCMLHnc79NI5ZpU',
            'access_token_jwt': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9',
        }

        # mock functions in order as in the code
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: True)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)
        monkeypatch.setattr(oauth.BaseOAuth2, 'auth_complete', mock_auth_complete)
        monkeypatch.setattr(web, 'generate_access_tokens', lambda x, y: tokens)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = core_user

        response = web.oauth_complete(request, 'github')
        data = json.loads(response.content)
        assert response.status_code == 200
        assert data == tokens

    @pytest.mark.django_db()
    def test_user_success(self, wsgi_request_factory, core_user, monkeypatch):
        def mock_auth_complete(*args, **kwargs):
            return core_user

        tokens = {
            'access_token': 'bZr9TVYykJnbVL1gAjq4Xhn3x1SY91',
            'expires_in': 36000,
            'token_type': 'Bearer',
            'scope': 'read write',
            'refresh_token': 'UDJsQxZpjVxhuOgrCMLHnc79NI5ZpU',
            'access_token_jwt': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9',
        }

        # mock functions in order as in the code
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)
        monkeypatch.setattr(oauth.BaseOAuth2, 'auth_complete', mock_auth_complete)
        monkeypatch.setattr(web, 'generate_access_tokens', lambda x, y: tokens)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        response = web.oauth_complete(request, 'github')
        data = json.loads(response.content)
        assert response.status_code == 200
        assert data == tokens

    @pytest.mark.django_db()
    def test_inactive_user(self, wsgi_request_factory, core_user, monkeypatch):
        core_user.is_active = False
        core_user.save()

        def mock_auth_complete(*args, **kwargs):
            return core_user

        # mock functions in order as in the code
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)
        monkeypatch.setattr(oauth.BaseOAuth2, 'auth_complete', mock_auth_complete)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        response = web.oauth_complete(request, 'github')
        assert response.status_code == 302
        assert response.url == settings.LOGIN_URL

    def test_no_auth_no_user(self, wsgi_request_factory, monkeypatch):
        def mock_auth_complete(*args, **kwargs):
            return None

        # mock functions in order as in the code
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)
        monkeypatch.setattr(oauth.BaseOAuth2, 'auth_complete', mock_auth_complete)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        response = web.oauth_complete(request, 'github')
        assert response.status_code == 302
        assert response.url == settings.LOGIN_URL

    @pytest.mark.xfail(raises=SocialAuthFailed)
    def test_backend_complete_xfail(self, wsgi_request_factory, monkeypatch):

        # mock functions
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)
        oauth.BaseOAuth2.auth_complete = Mock(side_effect=AuthFailed('github', [1]))

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        web.oauth_complete(request, 'github')

    @pytest.mark.xfail(raises=SocialAuthFailed)
    def test_without_code_xfail(self, wsgi_request_factory):

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()

        web.oauth_complete(request, 'github')

    @pytest.mark.xfail(raises=SocialAuthNotConfigured)
    def test_no_social_auth_redirect_url_xfail(
        self, settings, wsgi_request_factory, monkeypatch
    ):
        settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS['github'] = None

        # mock functions
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        web.oauth_complete(request, 'github')

    @pytest.mark.xfail(raises=SocialAuthNotConfigured)
    def test_no_support_social_auth_backend_xfail(
        self, settings, wsgi_request_factory, monkeypatch
    ):
        del settings.SOCIAL_AUTH_LOGIN_REDIRECT_URLS['github']

        # mock functions
        monkeypatch.setattr(web, 'user_is_authenticated', lambda x: False)
        monkeypatch.setattr(web, 'partial_pipeline_data', lambda x, y: None)

        # mock request object
        request = wsgi_request_factory()
        request.session = Mock()
        request.GET = {'code': 'test'}
        request.user = None

        web.oauth_complete(request, 'github')
