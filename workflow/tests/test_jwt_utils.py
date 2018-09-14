# -*- coding: utf-8 -*-
from django.test import TestCase
from django.test.client import RequestFactory
import factories

from ..jwt_utils import payload_enricher
from workflow.models import ROLE_SUPER_USER, ROLE_ORGANIZATION_ADMIN


class JWTUtilsTest(TestCase):
    def test_jwt_payload_enricher(self):
        rf = RequestFactory()
        tola_user = factories.CoreUser()
        request = rf.post('', {'username': tola_user.user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'user_uuid': str(tola_user.tola_user_uuid),
            'organization_uuid': str(tola_user.organization.organization_uuid),
            'role': None
        }
        self.assertEqual(payload, expected_payload)

    def test_jwt_payload_enricher_without_username(self):
        rf = RequestFactory()
        request = rf.post('', {})
        payload = payload_enricher(request)
        self.assertEqual(payload, {})

    def test_jwt_payload_enricher_superuser(self):
        rf = RequestFactory()
        tola_user = factories.CoreUser()
        tola_user.user.is_superuser = True
        tola_user.user.save()

        request = rf.post('', {'username': tola_user.user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'user_uuid': str(tola_user.tola_user_uuid),
            'organization_uuid': str(tola_user.organization.organization_uuid),
            'role': ROLE_SUPER_USER
        }
        self.assertEqual(payload, expected_payload)

    def test_jwt_payload_enricher_org_admin(self):
        rf = RequestFactory()
        tola_user = factories.CoreUser()
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        tola_user.user.groups.add(group_org_admin)

        request = rf.post('', {'username': tola_user.user.username})
        payload = payload_enricher(request)
        expected_payload = {
            'user_uuid': str(tola_user.tola_user_uuid),
            'organization_uuid': str(tola_user.organization.organization_uuid),
            'role': ROLE_ORGANIZATION_ADMIN
        }
        self.assertEqual(payload, expected_payload)
