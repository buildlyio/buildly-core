import pytest
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

import factories
from workflow import models as wfm

TEST_USER_DATA = {
    'first_name': 'John',
    'last_name': 'Snow',
    'email': 'test@example.com',
    'username': 'johnsnow',
    'password': '123qwe',
    'organization_name': 'Humanitec',
}


@pytest.fixture
def group_org_admin():
    return factories.Group.create(name=wfm.ROLE_ORGANIZATION_ADMIN)


@pytest.fixture
def org():
    return factories.Organization(name=TEST_USER_DATA['organization_name'])


@pytest.fixture
def org_member(org):
    return factories.CoreUser.create(organization=org)


@pytest.fixture
def org_admin(group_org_admin, org):
    coreuser = factories.CoreUser.create(organization=org)
    coreuser.groups.add(group_org_admin)
    return coreuser


@pytest.fixture
def reset_password_request(org_member):
    uid = urlsafe_base64_encode(force_bytes(org_member.pk)).decode()
    token = default_token_generator.make_token(org_member)
    return org_member, uid, token
