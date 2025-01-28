from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest
from django.http.request import HttpRequest
from django.utils.module_loading import import_string

from oauthlib.oauth2 import BearerToken
from oauth2_provider.models import Application
import jwt
from datetime import datetime, timedelta


def encode_jwt(payload, secret=settings.SECRET_KEY, algorithm='HS256'):
    return jwt.encode(payload, secret, algorithm=algorithm)


def generate_payload(issuer, expires_in, **extra_data):
    payload = {
        'iss': issuer,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow(),
    }
    payload.update(extra_data)
    return payload


def generate_access_tokens(request: WSGIRequest, user: User, client_id=None):
    import oauth2_provider.oauth2_validators
    # generate bearer token
    bearer_token = BearerToken(oauth2_provider.oauth2_validators.OAuth2Validator())
    request.scopes = ["read", "write"]
    request.state = None
    request.refresh_token = None
    request.extra_credentials = None
    request.user = user
    request.grant_type = ''
    try:
        # Fetch the application using the client_id
        if not client_id:
            client_id = settings.OAUTH_CLIENT_ID

        try:
            app = Application.objects.get(client_id=client_id)
        except Application.DoesNotExist:
            raise Exception("Application with the specified client_id does not exist.")
        if app.hash_client_secret:
            # Verify the client_secret using the `clean_client_secret` method
            if not check_password(settings.OAUTH_CLIENT_SECRET, app.client_secret):
                raise ValueError("Invalid client credentials.")
        else:
            # Verify the client_secret directly
            if settings.OAUTH_CLIENT_SECRET != app.client_secret:
                raise ValueError("Auth configuration problem: Please contact the administrator.")

        # The application is valid
        request.client = app

    except Application.DoesNotExist:
        raise Exception("Application with the specified client_id does not exist.")
    except ValueError:
        raise Exception("Invalid client credentials.")

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
