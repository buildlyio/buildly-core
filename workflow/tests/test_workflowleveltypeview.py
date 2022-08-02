import pytest
from rest_framework.reverse import reverse

import factories

from workflow.models import WorkflowLevelType
from ..views import WorkflowLevelTypeViewSet
from core.tests.fixtures import org_member, org

@pytest.mark.django_db()
def test_list_workflowleveltype(request_factory, org_member):
    request = request_factory.get(reverse('workflowleveltype-list'))
    request.user = org_member
    view = WorkflowLevelTypeViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_create_workflowleveltype(request_factory, org_member):
    data = {"name": "Test WFL Type"}
    request = request_factory.post(reverse('workflowleveltype-list'), data)
    request.user = org_member
    view = WorkflowLevelTypeViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 201


@pytest.mark.django_db()
def test_update_workflowleveltype(request_factory, org_member):
    wfltype = factories.WorkflowLevelType(name='change this')
    data = {"name": "Changed WFL Type Name"}
    request = request_factory.put('', data)
    request.user = org_member
    view = WorkflowLevelTypeViewSet.as_view({'put': 'update'})
    response = view(request, pk=wfltype.uuid)
    assert response.status_code == 200
    wfltype.refresh_from_db()
    assert wfltype.name == "Changed WFL Type Name"


@pytest.mark.django_db()
def test_delete_workflowleveltype(request_factory, org_member):
    wfltype = factories.WorkflowLevelType()
    request = request_factory.delete('')
    request.user = org_member
    view = WorkflowLevelTypeViewSet.as_view({'delete': 'destroy'})
    response = view(request, pk=wfltype.uuid)
    assert response.status_code == 204
    assert WorkflowLevelType.objects.count() == 0
