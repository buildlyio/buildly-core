from factory import DjangoModelFactory, SubFactory, Faker

from datamesh.models import (LogicModuleModel as LogicModulModelM,
                             Relationship as RelationshipM,
                             JoinRecord as JoinRecordM)
from factories import Organization
from gateway.models import LogicModule as LogicModuleM


class RandomLogicModule(DjangoModelFactory):
    name = Faker('word')

    class Meta:
        model = LogicModuleM


class LogicModuleModel(DjangoModelFactory):
    logic_module = SubFactory(RandomLogicModule)

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
    record_id = 1
    related_record_id = 2

    class Meta:
        model = JoinRecordM
