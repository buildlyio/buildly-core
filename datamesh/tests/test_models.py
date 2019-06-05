import uuid

import pytest
from django.db import IntegrityError, transaction

from datamesh.models import JoinRecord

from workflow.tests.fixtures import org
from .fixtures import relationship


@pytest.mark.django_db()
def test_create_join_record(relationship, org):
    JoinRecord.objects.create(
        relationship=relationship,
        record_id=1,
        related_record_id=2,
        organization=org,
    )
    JoinRecord.objects.create(
        relationship=relationship,
        record_uuid=uuid.uuid4(),
        related_record_uuid=uuid.uuid4(),
        organization=org,
    )
    assert JoinRecord.objects.count() == 2


@pytest.mark.django_db()
def test_one_record_primary_key_check_constraint_fail_empty_record_id_and_record_uuid(relationship, org):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                related_record_id=1,
                relationship=relationship,
                organization=org,
            )
    assert JoinRecord.objects.count() == 0


@pytest.mark.django_db()
def test_one_record_primary_key_check_constraint_fail_filled_id_and_uuid(relationship, org):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_id=1,
                record_uuid=1,
                relationship=relationship,
                organization=org,
            )
    assert JoinRecord.objects.count() == 0


@pytest.mark.django_db()
def test_one_record_primary_key_check_constraint_fail_empty_related_id_and_related_uuid(relationship, org):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_id=1,
                relationship=relationship,
                organization=org,
            )
    assert JoinRecord.objects.count() == 0


@pytest.mark.django_db()
def test_one_record_primary_key_check_constraint_fail_filled_related_id_and_related_uuid(relationship, org):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                related_record_id=1,
                related_record_uuid=1,
                relationship=relationship,
                organization=org,
            )
    assert JoinRecord.objects.count() == 0
