import jwt

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings


class CustomJWTAuthentication(BaseAuthentication):
    """
    Custom JWT authentication class that validates and authenticates users
    based on the token generated from the generate_access_tokens function.
    """

    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split('Bearer ')[1]

        try:
            # Decode the token
            payload = jwt.decode(token, settings.TOKEN_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed("Invalid token")

        try:
            # Retrieve the user from the database
            user = get_user_model().objects.get(core_user_uuid=payload.get('core_user_uuid'))
        except get_user_model().DoesNotExist:
            raise AuthenticationFailed("User not found")

        return (user, token)

    def authenticate_header(self, request):
        return 'Bearer'
