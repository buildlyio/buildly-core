# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
import factories

from ..jwt_utils import payload_enricher
from workflow.models import ROLE_ORGANIZATION_ADMIN


class JWTUtilsTest(TestCase):

    def setUp(self) -> None:
        self.rf = RequestFactory()
        self.core_user = factories.CoreUser()

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
