import pytest

from datamesh.serializers import JoinRecordSerializer
from .fixtures import join_record


@pytest.mark.django_db()
def test_join_record_serializer_from_instance(request_factory, join_record):
    request = request_factory.get('')
    request.session = {
        'jwt_organization_uuid': join_record.organization.organization_uuid
    }
    serializer = JoinRecordSerializer(
        instance=join_record, context={'request': request}
    )
    keys = [
        "join_record_uuid",
        "record_id",
        "record_uuid",
        "related_record_id",
        "related_record_uuid",
        "organization",
        "origin_model_name",
        "related_model_name",
    ]
    data = serializer.data
    assert set(data.keys()) == set(keys)
    assert data['organization'] == join_record.organization.organization_uuid
