import pytest

from workflow.serializers import WorkflowLevel2Serializer, WorkflowLevelTypeSerializer
from .fixtures import wfl2, wfl_type

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
