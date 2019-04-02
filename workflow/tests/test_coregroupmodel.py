import pytest
import factories


@pytest.mark.django_db()
def test_coregroup_display_permissions():
    for i in range(16):
        coregroup = factories.CoreGroup.create(permissions=i)
        assert len(coregroup.display_permissions) == 4
        assert coregroup.display_permissions == f'{i:04b}'

    coregroup = factories.CoreGroup.create(permissions=20)
    assert coregroup.display_permissions == '1111'
