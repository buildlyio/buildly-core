import uuid
from unittest.mock import Mock

import pytest
from pyswagger.io import Response as PySwaggerResponse

import factories


@pytest.fixture
def join_record():
    return factories.JoinRecord()


@pytest.fixture
def relationship():
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lmm = factories.LogicModuleModel(logic_module=lm, model='Product', endpoint='/products/')
    lm_document = factories.LogicModule(name='Document Service', endpoint_name='documents')
    lmm_document = factories.LogicModuleModel(logic_module=lm_document, model='Document', endpoint='/documents/')
    return factories.Relationship(origin_model=lmm, related_model=lmm_document, key='document_relationship')


@pytest.fixture
def relationship2(relationship):
    lmm = relationship.origin_model  # Products model from 1st relationship
    lm_location = factories.LogicModule(name='Location Service', endpoint_name='location')
    lmm_location = factories.LogicModuleModel(logic_module=lm_location, model='Location', endpoint='/siteprofile/')
    return factories.Relationship(origin_model=lmm, related_model=lmm_location, key='location_relationship')


@pytest.fixture
def relationship_with_10_records():
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lmm = factories.LogicModuleModel(logic_module=lm, model='Product', endpoint='/products/', lookup_field_name='uuid')
    lm_document = factories.LogicModule(name='Document Service', endpoint_name='documents')
    lmm_document = factories.LogicModuleModel(logic_module=lm_document, model='Document', endpoint='/documents/',
                                              lookup_field_name='uuid')
    relationship = factories.Relationship(origin_model=lmm, related_model=lmm_document, key='document_relationship')
    for _ in range(10):
        factories.JoinRecord.create(relationship=relationship,
                                    record_uuid=uuid.uuid4(), record_id=None,
                                    related_record_uuid=uuid.uuid4(), related_record_id=None)
    return relationship


@pytest.fixture
def logic_module_model():
    return factories.LogicModuleModel()


def service_response_mock(data):
    headers = {'Content-Type': ['application/json']}
    service_response = Mock(PySwaggerResponse)
    service_response.status = 200
    service_response.header = headers
    service_response.data = data
    return service_response

