import pytest
from rest_framework.reverse import reverse

from workflow.views import PermissionViewSet
from .fixtures import org, org_member


@pytest.mark.django_db()
def test_permissions_list_forbidden(request_factory):
    request = request_factory.get(reverse('permission-list'))
    response = PermissionViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 403


@pytest.mark.django_db()
def test_permissions_list(request_factory, org_member):
    request = request_factory.get(reverse('permission-list'))
    request.user = org_member
    response = PermissionViewSet.as_view({'get': 'list'})(request)
    assert response.status_code == 200


@pytest.mark.django_db()
def test_permissions_create_fail(request_factory, org_member):
    request = request_factory.post(reverse('permission-list'))
    request.user = org_member
    with pytest.raises(AttributeError):
        response = PermissionViewSet.as_view({'post': 'create'})(request)
