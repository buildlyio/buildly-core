import pytest

from core.serializers import OrganizationSerializer, CoreGroupSerializer, CoreUserSerializer
from core.tests.fixtures import core_group, org, org_member


@pytest.mark.django_db()
def test_org_serializer(request_factory, org):
    request = request_factory.get('')
    serializer = OrganizationSerializer(org, context={'request': request})
    data = serializer.data
    keys = ['id',
            'organization_uuid',
            'name',
            'description',
            'organization_url',
            'create_date',
            'edit_date',
            'oauth_domains',
            'date_format',
            'phone',
            'industries',
            'stripe_subscription_details',
            ]
    assert set(data.keys()) == set(keys)


@pytest.mark.django_db()
def test_core_groups_serializer(request_factory, core_group):
    request = request_factory.get('')
    serializer = CoreGroupSerializer(core_group, context={'request': request})
    data = serializer.data
    keys = ['id',
            'uuid',
            'name',
            'is_global',
            'is_org_level',
            'permissions',
            'organization',
            'workflowlevel1s',
            'workflowlevel2s',
            ]
    assert set(data.keys()) == set(keys)
    assert isinstance(data['organization'], str)


@pytest.mark.django_db()
def test_core_user_serializer(request_factory, org_member):
    request = request_factory.get('')
    serializer = CoreUserSerializer(org_member, context={'request': request})
    data = serializer.data
    keys = ['id',
            'core_user_uuid',
            'first_name',
            'last_name',
            'email',
            'username',
            'is_active',
            'title',
            'contact_info',
            'privacy_disclaimer_accepted',
            'organization',
            'core_groups',
            'user_type',
            'survey_status'
            ]
    assert set(data.keys()) == set(keys)
    assert isinstance(data['organization'], dict)
