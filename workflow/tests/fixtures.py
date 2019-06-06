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
def org():
    return factories.Organization(name=TEST_USER_DATA['organization_name'])


@pytest.fixture
def org_member(org):
    return factories.CoreUser.create(organization=org)


@pytest.fixture
def core_group(org):
    return factories.CoreGroup(organization=org)


@pytest.fixture
def org_admin(org):
    group_org_admin, _ = wfm.CoreGroup.objects.get_or_create(organization=org, is_org_level=True,
                                                             permissions=wfm.PERMISSIONS_ORG_ADMIN,
                                                             defaults={'name':'Org Admin'})
    coreuser = factories.CoreUser.create(organization=group_org_admin.organization)
    coreuser.core_groups.add(group_org_admin)
    return coreuser


@pytest.fixture
def reset_password_request(org_member):
    uid = urlsafe_base64_encode(force_bytes(org_member.pk))
    token = default_token_generator.make_token(org_member)
    return org_member, uid, token
