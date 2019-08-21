import pytest
from rest_framework.reverse import reverse

import factories

from workflow.models import WorkflowLevelStatus, WorkflowLevel2
from ..views import WorkflowLevelStatusViewSet
from .fixtures import org_member, org


@pytest.mark.django_db()
def test_list_workflowlevelstatus(request_factory, org_member):
    request = request_factory.get(reverse('workflowlevelstatus-list'))
    request.user = org_member
    view = WorkflowLevelStatusViewSet.as_view({'get': 'list'})
    response = view(request)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_create_workflowlevelstatus(request_factory, org_member):
    data = {"name": "Test WFL Status", "short_name": "test_status"}
    request = request_factory.post('', data)
    request.user = org_member
    view = WorkflowLevelStatusViewSet.as_view({'post': 'create'})
    response = view(request)
    assert response.status_code == 201


@pytest.mark.django_db()
def test_update_workflowlevelstatus(request_factory, org_member):
    wflstatus = factories.WorkflowLevelStatus(name='change this')
    data = {"name": "Changed WFL Status Name",
            "short_name": "changed"}
    request = request_factory.put('', data)
    request.user = org_member
    view = WorkflowLevelStatusViewSet.as_view({'put': 'update'})
    response = view(request, pk=wflstatus.uuid)
    assert response.status_code == 200
    wflstatus.refresh_from_db()
    assert wflstatus.name == "Changed WFL Status Name"
    assert wflstatus.short_name == "changed"


@pytest.mark.django_db()
def test_delete_workflowlevelstatus(request_factory, org_member):
    wflstatus = factories.WorkflowLevelStatus()
    request = request_factory.delete('')
    request.user = org_member
    view = WorkflowLevelStatusViewSet.as_view({'delete': 'destroy'})
    response = view(request, pk=wflstatus.uuid)
    assert response.status_code == 204


@pytest.mark.django_db()
def test_create_workflowlevel2_with_default_status(request_factory, org_member):
    wfl1 = factories.WorkflowLevel1()
    wfl2 = WorkflowLevel2.objects.create(workflowlevel1=wfl1)
    assert wfl2.status.short_name == 'project_request'
