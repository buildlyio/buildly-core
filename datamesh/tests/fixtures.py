import pytest

import factories


@pytest.fixture
def join_record():
    return factories.JoinRecord()


@pytest.fixture
def relationship():
    lm = factories.LogicModule(name='Products Service', endpoint_name='products')
    lm_document = factories.LogicModule(name='Document Service', endpoint_name='documents')
    lmm = factories.LogicModuleModel(logic_module=lm, model='Product', endpoint='/products/')
    lmm_document = factories.LogicModuleModel(logic_module=lm_document, model='Document', endpoint='/documents/')
    return factories.Relationship(origin_model=lmm, related_model=lmm_document, key='document_relationship')


@pytest.fixture
def logic_module_model():
    return factories.LogicModuleModel()
