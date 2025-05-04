import uuid

import pytest

import factories


@pytest.fixture
def join_record():
    return factories.JoinRecord()


@pytest.fixture
def relationship():
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lmm = factories.LogicModuleModel(
        logic_module_endpoint_name=lm.endpoint_name,
        model='Product',
        endpoint='/products/',
    )
    lm_document = factories.LogicModule(
        name='Document Service', endpoint_name='documents'
    )
    lmm_document = factories.LogicModuleModel(
        logic_module_endpoint_name=lm_document.endpoint_name,
        model='Document',
        endpoint='/documents/',
    )
    return factories.Relationship(
        origin_model=lmm,
        related_model=lmm_document,
        key='product_document_relationship',
    )


@pytest.fixture
def relationship2(relationship):
    lmm = relationship.origin_model  # Products model from 1st relationship
    lm_location = factories.LogicModule(
        name='Location Service', endpoint_name='location'
    )
    lmm_location = factories.LogicModuleModel(
        logic_module_endpoint_name=lm_location.endpoint_name,
        model='Location',
        endpoint='/siteprofile/',
    )
    return factories.Relationship(
        origin_model=lmm, related_model=lmm_location, key='location_relationship'
    )


@pytest.fixture
def relationship_with_10_records(org):
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lmm = factories.LogicModuleModel(
        logic_module_endpoint_name=lm.endpoint_name,
        model='Product',
        endpoint='/products/',
        lookup_field_name='uuid',
    )
    lm_document = factories.LogicModule(
        name='Document Service', endpoint_name='documents'
    )
    lmm_document = factories.LogicModuleModel(
        logic_module_endpoint_name=lm_document.endpoint_name,
        model='Document',
        endpoint='/documents/',
        lookup_field_name='uuid',
    )
    relationship = factories.Relationship(
        origin_model=lmm,
        related_model=lmm_document,
        key='product_document_relationship',
    )
    for _ in range(10):
        factories.JoinRecord.create(
            relationship=relationship,
            record_uuid=uuid.uuid4(),
            record_id=None,
            related_record_uuid=uuid.uuid4(),
            related_record_id=None,
            organization=org,
        )
    return relationship


@pytest.fixture
def relationship_with_local():
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lmm = factories.LogicModuleModel(
        logic_module_endpoint_name=lm.endpoint_name,
        model='Product',
        endpoint='/products/',
    )
    lmm_org = factories.LogicModuleModel(
        logic_module_endpoint_name='core',
        model='Organization',
        endpoint='/organization/',
        lookup_field_name='organization_uuid',
        is_local=True,
    )
    return factories.Relationship(
        origin_model=lmm, related_model=lmm_org, key='product_document_relationship'
    )


@pytest.fixture
def document_logic_module():
    return factories.LogicModule(name='document', endpoint_name='document')


@pytest.fixture
def crm_logic_module():
    return factories.LogicModule(name='crm', endpoint_name='crm')


@pytest.fixture
def logic_module_model():
    return factories.LogicModuleModel()


@pytest.fixture
def document_logic_module_model():
    return factories.LogicModuleModel(
        logic_module_endpoint_name='document', model='Document'
    )


@pytest.fixture
def appointment_logic_module_model():
    return factories.LogicModuleModel(
        logic_module_endpoint_name='crm', model='Appointment'
    )
