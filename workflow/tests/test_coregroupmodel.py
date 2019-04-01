import pytest
import factories
from workflow.models import CoreGroup
from .fixtures import org


@pytest.mark.django_db()
def test_coregroup_with_wfl1_organization(org):
    wfl1 = factories.WorkflowLevel1.create(organization=org, name='Program')
    coregroup = CoreGroup(workflowlevel1=wfl1, name='Program Admin')
    coregroup.save()
    created = CoreGroup.objects.get(name='Program Admin')
    assert created.organization == org


@pytest.mark.django_db()
def test_coregroup_with_wfl2_organization(org):
    wfl1 = factories.WorkflowLevel1.create(organization=org, name='Program')
    wfl2 = factories.WorkflowLevel2.create(workflowlevel1=wfl1, name='Project')
    coregroup = CoreGroup(workflowlevel2=wfl2, name='Project Admin')
    coregroup.save()
    created = CoreGroup.objects.get(name='Project Admin')
    assert created.organization == org


@pytest.mark.django_db()
def test_coregroup_with_no_wfl():
    coregroup = CoreGroup(name='Organization Admin')
    coregroup.save()
    created = CoreGroup.objects.get(name='Organization Admin')
    assert created.organization is None


@pytest.mark.django_db()
def test_coregroup_display_permissions():
    for i in range(16):
        coregroup = factories.CoreGroup.create(permissions=i)
        assert len(coregroup.display_permissions) == 4
        assert coregroup.display_permissions == f'{i:04b}'

    coregroup = factories.CoreGroup.create(permissions=20)
    assert coregroup.display_permissions == '1111'
