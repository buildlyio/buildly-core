from django.conf import settings
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import HttpRequest
from django.utils.module_loading import import_string

from oauthlib.oauth2 import BearerToken
from oauth2_provider.models import Application
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauth2_provider_jwt.utils import encode_jwt, generate_payload


def generate_access_tokens(request: WSGIRequest, user: User):
    # generate bearer token
    bearer_token = BearerToken(OAuth2Validator())
    request.scopes = ["read", "write"]
    request.state = None
    request.refresh_token = None
    request.extra_credentials = None
    request.user = user
    request.grant_type = ''
    request.client = Application.objects.get(
        client_id=settings.OAUTH_CLIENT_ID, client_secret=settings.OAUTH_CLIENT_SECRET
    )
    token = bearer_token.create_token(request, refresh_token=True)
    bearer_token.request_validator.save_bearer_token(token, request)

    # generate JWT
    issuer = settings.JWT_ISSUER
    payload_enricher = getattr(settings, 'JWT_PAYLOAD_ENRICHER', None)
    extra_data = {'username': user.username} if user else {}
    jwt_request = HttpRequest()
    jwt_request.POST = extra_data
    if payload_enricher:
        fn = import_string(payload_enricher)
        extra_data.update(fn(jwt_request))
    payload = generate_payload(issuer, token['expires_in'], **extra_data)
    token['access_token_jwt'] = encode_jwt(payload)

    return token
