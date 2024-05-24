import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django.utils import timezone

import factories
from oauth2_provider.models import (
    get_application_model,
    get_access_token_model,
    get_refresh_token_model,
)

from core.jwt_utils import payload_enricher
from core.models import ROLE_ORGANIZATION_ADMIN


AccessToken = get_access_token_model()
RefreshToken = get_refresh_token_model()
Application = get_application_model()


class JWTUtilsTest(TestCase):
    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.core_user = factories.CoreUser()

        # for testing refresh token
        application = Application(
            name="Test JWT Application",
            user=self.core_user,
            client_type=Application.CLIENT_PUBLIC,
            authorization_grant_type=Application.GRANT_PASSWORD,
        )
        application.save()
        access_token = AccessToken.objects.create(
            user=self.core_user,
            token="1234567890",
            application=application,
            expires=timezone.now() + datetime.timedelta(days=1),
            scope="read write",
        )
        RefreshToken.objects.create(
            access_token=access_token,
            user=self.core_user,
            application=application,
            token="007",
        )

    def test_jwt_payload_enricher(self):
        request = self.rf.post('', {'username': self.core_user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'core_user_uuid': str(self.core_user.core_user_uuid),
            'organization_uuid': str(self.core_user.organization.organization_uuid),
        }
        self.assertEqual(payload, expected_payload)

    def test_jwt_payload_enricher_without_username(self):
        rf = RequestFactory()
        request = rf.post('', {})
        payload = payload_enricher(request)
        self.assertEqual(payload, {})

    def test_jwt_payload_enricher_superuser(self):
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.rf.post('', {'username': self.core_user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'core_user_uuid': str(self.core_user.core_user_uuid),
            'organization_uuid': str(self.core_user.organization.organization_uuid),
        }
        self.assertEqual(payload, expected_payload)

    def test_jwt_payload_enricher_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.groups.add(group_org_admin)

        request = self.rf.post('', {'username': self.core_user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'core_user_uuid': str(self.core_user.core_user_uuid),
            'organization_uuid': str(self.core_user.organization.organization_uuid),
        }
        self.assertEqual(payload, expected_payload)

    def test_jwt_payload_enricher_refresh_token(self):
        request = self.rf.post('', {'refresh_token': "007"})
        payload = payload_enricher(request)
        expected_payload = {
            'core_user_uuid': str(self.core_user.core_user_uuid),
            'organization_uuid': str(self.core_user.organization.organization_uuid),
            'username': self.core_user.username,
        }
        self.assertEqual(payload, expected_payload)
