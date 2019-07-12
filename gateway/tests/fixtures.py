import pytest

import factories


@pytest.fixture()
def logic_module():
    return factories.LogicModule.create(name='documents',
                                        endpoint_name='documents',
                                        endpoint='http://documentservice:8080')
