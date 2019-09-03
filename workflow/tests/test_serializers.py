import pytest

from workflow.serializers import OrganizationSerializer, CoreGroupSerializer, CoreUserSerializer, \
    WorkflowLevel2Serializer, WorkflowLevelTypeSerializer
from .fixtures import org, core_group, org_member, wfl2, wfl_type


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
            'level_1_label',
            'level_2_label',
            'level_3_label',
            'level_4_label',
            'create_date',
            'edit_date',
            'subscription_id',
            'used_seats',
            'oauth_domains',
            'date_format',
            'phone',
            'industries',
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
            'create_date',
            ]
    assert set(data.keys()) == set(keys)
    assert isinstance(data['organization'], dict)


@pytest.mark.django_db()
def test_workflow_level2_serializer(request_factory, wfl2):
    request = request_factory.get('')
    serializer = WorkflowLevel2Serializer(wfl2, context={'request': request})
    data = serializer.data
    keys = ["id",
            "level2_uuid",
            "description",
            "name",
            "notes",
            "parent_workflowlevel2",
            "short_name",
            "create_date",
            "edit_date",
            "start_date",
            "end_date",
            "workflowlevel1",
            "created_by",
            "type",
            "core_groups",
            "status",
            # "project_id",  # TODO: set back after FE has migrated
            ]
    assert set(data.keys()) == set(keys)
    assert data["id"] == data["level2_uuid"]


@pytest.mark.django_db()
def test_workflow_level_type_serializer(request_factory, wfl_type):
    request = request_factory.get('')
    serializer = WorkflowLevelTypeSerializer(wfl_type, context={'request': request})
    data = serializer.data
    keys = ["id",
            "uuid",
            "name",
            "create_date",
            "edit_date",
            ]
    assert set(data.keys()) == set(keys)
    assert data["id"] == data["uuid"]
