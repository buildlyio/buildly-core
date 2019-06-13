import pytest

import factories


@pytest.fixture
def join_record():
    return factories.JoinRecord()


@pytest.fixture
def relationship():
    return factories.Relationship()


@pytest.fixture
def logic_module_model():
    return factories.LogicModuleModel()
