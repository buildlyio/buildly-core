import pytest

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
    coreuser.user.groups.add(group_org_admin)
    return coreuser
