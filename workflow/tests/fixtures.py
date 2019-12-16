import pytest

import factories


@pytest.fixture
def wfl2():
    return factories.WorkflowLevel2()


@pytest.fixture
def wfl_type():
    return factories.WorkflowLevelType()
