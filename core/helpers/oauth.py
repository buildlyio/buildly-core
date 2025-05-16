from datetime import datetime, timedelta
from urllib.parse import urljoin

import itsdangerous

import jwt
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from django.conf import settings

from core.email_utils import send_email
from core.models import CoreUser


class EmailVerificationToken:
    class TokenExpiredException(Exception):
        code = 'token_expired'
        message = 'Token expired'

    class InvalidTokenException(Exception):
        code = 'invalid_token'
        message = 'Invalid token'

    # Create a serializer for signing the token
    token_serializer = itsdangerous.URLSafeTimedSerializer(settings.SECRET_KEY)

    EMAIL_VERIFICATION_EXPIRATION = timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRATION)
    MAX_AGE_SECONDS = int(EMAIL_VERIFICATION_EXPIRATION.total_seconds())

    def generate_email_verification_token(self, user: CoreUser):
        """
        Generates a secure, time-limited token containing the user's ID.
        """
        return self.token_serializer.dumps(f'{user.core_user_uuid}')

    def verify_email_token(self, token):  # Token expires in 30 minutes
        """
        Decodes the verification token and extracts the user ID.
        """
        try:
            user_id = self.token_serializer.loads(
                token,
                max_age=self.MAX_AGE_SECONDS
            )
            return user_id

        except itsdangerous.SignatureExpired:
            raise self.TokenExpiredException()

        except itsdangerous.BadSignature:
            raise self.InvalidTokenException()

    def extract_user_id_from_token(self, token):
        """
        Extracts the user ID from a token, even if expired.
        """
        if not token:
            return None

        # Try loading token with expiration enforcement
        try:
            return self.token_serializer.loads(token, max_age=None)
        except itsdangerous.BadSignature:
            raise self.InvalidTokenException()

    def send_verification_email(self, request, core_user: CoreUser):
        # create or update an invitation
        reg_location = urljoin(settings.FRONTEND_URL, settings.VERIFY_EMAIL_URL_PATH)
        token = self.generate_email_verification_token(core_user)
        reg_location = f'{reg_location}?token={token}'

        # build the invitation link
        verification_link = request.build_absolute_uri(reg_location)

        # create the user context for the E-mail templates
        context = {
            'verification_link': verification_link,
            'user': core_user,
        }
        subject = 'Account verification required'  # TODO we need to make this dynamic
        template_name = 'email/coreuser/email_verification.txt'
        html_template_name = 'email/coreuser/email_verification.html'
        send_email(core_user.email, subject, context, template_name, html_template_name)
