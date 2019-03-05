import pytest
from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse

import factories
from workflow import models as wfm
from workflow.views import CoreGroupViewSet
from .fixtures import org, org_admin, org_member, group_org_admin


@pytest.mark.django_db()
class TestCoreUserViewsPermissions:

    def test_coreuser_views_permissions_unauth(self, request_factory):
        pass

    def test_coreuser_views_permissions_org_member(self, request_factory, org_member):
        pass

    def test_coreuser_views_permissions_different_org_member(self, request_factory, org_member):
        pass

    def test_coreuser_views_permissions_different_org_admin(self, request_factory, org_admin):
        pass


@pytest.mark.django_db()
class TestCoreUserCreateView:

    def test_coregroup_create_fail(self, request_factory, org_admin):
        data = {'group':  {}}
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_coregroup_create_min(self, request_factory, org_admin):
        data = {'group': {'name': 'New Group'}}
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        assert wfm.CoreGroup.objects.get(group__name='New Group')

    def test_coregroup_create(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        data = {
            'group': {'name': 'New Group'},
            'organization': org_admin.organization.pk,
            'workflowlevel1': wfl1.pk,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(group__name='New Group')
        assert coregroup.organization == org_admin.organization

    def test_coregroup_create_with_permissions(self, request_factory, org_admin):
        permissions = Permission.objects.values_list('id', flat=True)[:2]
        data = {
            'group': {'name': 'New Group', 'permissions': permissions},
            'organization': org_admin.organization.pk,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(group__name='New Group')
        assert len(coregroup.group.permissions.all()) == 2
        assert set(permissions) == set(coregroup.group.permissions.values_list('id', flat=True))


@pytest.mark.django_db()
class TestCoreUserUpdateView:
    def test_coregroup_update(self, request_factory, org_admin):
        pass


@pytest.mark.django_db()
class TestCoreUserListView:
    pass


@pytest.mark.django_db()
class TestCoreUserDetailView:
    pass
