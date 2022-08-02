import uuid

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from datamesh.models import JoinRecord, Relationship, LogicModuleModel
from core.tests.fixtures import org
from .fixtures import relationship, appointment_logic_module_model, document_logic_module_model


@pytest.mark.django_db()
def test_fail_create_reverse_relationship(relationship):
    with pytest.raises(ValidationError):
        Relationship.objects.create(
            related_model=relationship.origin_model,
            origin_model=relationship.related_model
        )


@pytest.mark.django_db()
def test_get_by_concatenated_model_name(appointment_logic_module_model, document_logic_module_model):
    lmm = LogicModuleModel.objects.get_by_concatenated_model_name("crmAppointment")
    assert lmm == appointment_logic_module_model
    assert None == LogicModuleModel.objects.get_by_concatenated_model_name("nothing")


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


@pytest.mark.django_db()
def test_unique_together_join_record_id_id(relationship, org):
    JoinRecord.objects.create(
        record_id=1,
        related_record_id=1,
        relationship=relationship,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_id=1,
                related_record_id=1,
                relationship=relationship,
            )
    assert JoinRecord.objects.count() == 1


@pytest.mark.django_db()
def test_unique_together_join_record_uuid_uuid(relationship, org):
    JoinRecord.objects.create(
        record_uuid=1,
        related_record_uuid=1,
        relationship=relationship,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_uuid=1,
                related_record_uuid=1,
                relationship=relationship,
            )
    assert JoinRecord.objects.count() == 1


@pytest.mark.django_db()
def test_unique_together_join_record_id_uuid(relationship, org):
    JoinRecord.objects.create(
        record_id=1,
        related_record_uuid=1,
        relationship=relationship,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_id=1,
                related_record_uuid=1,
                relationship=relationship,
            )
    assert JoinRecord.objects.count() == 1


@pytest.mark.django_db()
def test_unique_together_join_record_uuid_id(relationship, org):
    JoinRecord.objects.create(
        record_uuid=1,
        related_record_id=1,
        relationship=relationship,
    )
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            JoinRecord.objects.create(
                record_uuid=1,
                related_record_id=1,
                relationship=relationship,
            )
    assert JoinRecord.objects.count() == 1
