import uuid

import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

import factories
from core.models import PERMISSIONS_ORG_ADMIN

TEST_USER_DATA = {
    'first_name': 'John',
    'last_name': 'Snow',
    'email': 'test@example.com',
    'username': 'johnsnow',
    'password': '123qwe',
    'organization_name': 'buidly',
    'organization_uuid': uuid.uuid4(),
}


@pytest.fixture
def superuser():
    return factories.CoreUser.create(is_superuser=True)


@pytest.fixture
def org():
    return factories.Organization(
        name=TEST_USER_DATA['organization_name'],
        organization_uuid=TEST_USER_DATA['organization_uuid'],
    )


@pytest.fixture
def org_member(org):
    return factories.CoreUser.create(organization=org)


@pytest.fixture
def core_group(org):
    return factories.CoreGroup(organization=org)


@pytest.fixture
def org_admin(org):
    group_org_admin = factories.CoreGroup(name='Org Admin', organization=org, is_org_level=True,
                                          permissions=PERMISSIONS_ORG_ADMIN)
    coreuser = factories.CoreUser.create(organization=group_org_admin.organization)
    coreuser.core_groups.add(group_org_admin)
    return coreuser


@pytest.fixture
def reset_password_request(org_member):
    uid = urlsafe_base64_encode(force_bytes(org_member.pk))
    token = default_token_generator.make_token(org_member)
    return org_member, uid, token


@pytest.fixture
def auth_api_client():
    api_client = APIClient()
    api_client.force_authenticate(user=factories.CoreUser.create())
    return api_client


@pytest.fixture
def auth_superuser_api_client(superuser):
    api_client = APIClient()
    api_client.force_authenticate(user=superuser)
    return api_client


@pytest.fixture
def oauth_application():
    return factories.Application()


@pytest.fixture
def oauth_access_token():
    return factories.AccessToken()


@pytest.fixture
def oauth_refresh_token():
    return factories.RefreshToken()


@pytest.fixture()
def logic_module():
    return factories.LogicModule.create(name='documents',
                                        endpoint_name='documents',
                                        endpoint='http://documentservice:8080')


@pytest.fixture()
def datamesh():
    lm1 = factories.LogicModule.create(name='location', endpoint_name='location',
                                       endpoint='http://locationservice:8080')
    lm2 = factories.LogicModule.create(name='documents', endpoint_name='documents',
                                       endpoint='http://documentservice:8080')
    lmm1 = factories.LogicModuleModel(logic_module_endpoint_name=lm1.endpoint_name, model='SiteProfile',
                                      endpoint='/siteprofiles/', lookup_field_name='uuid')
    lmm2 = factories.LogicModuleModel(logic_module_endpoint_name=lm2.endpoint_name, model='Document',
                                      endpoint='/documents/', lookup_field_name='id')
    relationship = factories.Relationship(origin_model=lmm1, related_model=lmm2, key='documents')
    return lm1, lm2, relationship
