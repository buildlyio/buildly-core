import random
import string
import uuid

from factory import DjangoModelFactory, SubFactory, LazyAttribute

from datamesh.models import (
    LogicModuleModel as LogicModulModelM,
    Relationship as RelationshipM,
    JoinRecord as JoinRecordM,
)
from factories import Organization


class LogicModuleModel(DjangoModelFactory):
    logic_module_endpoint_name = LazyAttribute(
        lambda o: ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    )
    lookup_field_name = 'id'

    class Meta:
        model = LogicModulModelM


class Relationship(DjangoModelFactory):
    origin_model = SubFactory(LogicModuleModel)
    related_model = SubFactory(LogicModuleModel)

    class Meta:
        model = RelationshipM


class JoinRecord(DjangoModelFactory):
    relationship = SubFactory(Relationship)
    organization = SubFactory(Organization)
    record_id = LazyAttribute(lambda x: random.randrange(0, 10000))
    related_record_uuid = LazyAttribute(lambda o: uuid.uuid4())

    class Meta:
        model = JoinRecordM
