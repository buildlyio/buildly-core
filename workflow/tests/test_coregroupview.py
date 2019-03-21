import pytest
from django.contrib.auth.models import Permission
from rest_framework.reverse import reverse

import factories
from workflow import models as wfm
from workflow.views import CoreGroupViewSet
from .fixtures import org, org_admin, org_member, group_org_admin


@pytest.mark.django_db()
class TestCoreGroupViewsPermissions:

    def test_coregroup_views_permissions_unauth(self, request_factory):
        request = request_factory.get(reverse('coregroup-list'))
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 403

        request = request_factory.post(reverse('coregroup-list'))
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 403

        request = request_factory.get(reverse('coregroup-detail', args=(1,)))
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.put(reverse('coregroup-detail', args=(1,)))
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.patch(reverse('coregroup-detail', args=(1,)))
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.delete(reverse('coregroup-detail', args=(1,)))
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        assert response.status_code == 403

    def test_coregroup_views_permissions_org_member(self, request_factory, org_member):
        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 403

        request = request_factory.post(reverse('coregroup-list'))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 403

        request = request_factory.get(reverse('coregroup-detail', args=(1,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.put(reverse('coregroup-detail', args=(1,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.patch(reverse('coregroup-detail', args=(1,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.delete(reverse('coregroup-detail', args=(1,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        assert response.status_code == 403

    def test_coregroup_views_permissions_different_org_admin(self, request_factory, org, group_org_admin):
        coregroup = factories.CoreGroup.create(organization=org)

        # create admin of another organization
        coreuser = factories.CoreUser.create(organization=factories.Organization(name='Another Org'))
        coreuser.groups.add(group_org_admin)

        request = request_factory.get(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = coreuser
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=coregroup.pk)
        assert response.status_code == 403

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = coreuser
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 403

        request = request_factory.patch(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = coreuser
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=coregroup.pk)
        assert response.status_code == 403

        request = request_factory.delete(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = coreuser
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=coregroup.pk)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestCoreGroupCreateView:

    def test_coregroup_create_fail(self, request_factory, org_admin):
        request = request_factory.post(reverse('coregroup-list'), {}, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_coregroup_create_min(self, request_factory, org_admin):
        data = {'name': 'New Group'}
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(name='New Group')
        assert coregroup.organization == org_admin.organization

    def test_coregroup_create_with_permissions(self, request_factory, org_admin):
        permissions = Permission.objects.values_list('id', flat=True)[:2]
        data = {
            'name': 'New Group',
            'permissions': permissions,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(name='New Group')
        assert len(coregroup.permissions.all()) == 2
        assert set(permissions) == set(coregroup.permissions.values_list('id', flat=True))


@pytest.mark.django_db()
class TestCoreGroupUpdateView:

    def test_coregroup_update(self, request_factory, org_admin):
        permissions = Permission.objects.values_list('id', flat=True)[:3]
        coregroup = factories.CoreGroup.create(organization=org_admin.organization)
        coregroup.permissions.set(permissions[:2])  # 1st and 2nd permissions

        data = {
            'name': 'Updated Name',
            'permissions': permissions[1:],  # 2nd and 3rd permissions
        }

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        coregroup_upd = wfm.CoreGroup.objects.get(pk=coregroup.pk)
        assert coregroup_upd.name == 'Updated Name'
        assert set(permissions[1:]) == set(coregroup_upd.permissions.values_list('id', flat=True))


@pytest.mark.django_db()
class TestCoreGroupListView:

    def test_coregroup_list(self, request_factory, org_admin):
        factories.CoreGroup.create(name='Group 1', organization=org_admin.organization)
        factories.CoreGroup.create(name='Group 2', organization=org_admin.organization)
        factories.CoreGroup.create(name='Group 3', organization=factories.Organization(name='Another org'))

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db()
class TestCoreGroupDetailView:

    def test_coregroup_detail(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(organization=org_admin.organization)
        coregroup.permissions.set(Permission.objects.values_list('id', flat=True)[:2])

        request = request_factory.get(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        assert response.data['organization'] == org_admin.organization.id
        assert len(response.data['permissions']) == 2


@pytest.mark.django_db()
class TestCoreGroupDeleteView:

    def test_coregroup_detete(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(organization=org_admin.organization)
        coregroup.permissions.set(Permission.objects.values_list('id', flat=True)[:2])

        request = request_factory.delete(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=coregroup.pk)
        assert response.status_code == 204

        with pytest.raises(wfm.CoreGroup.DoesNotExist):
            wfm.CoreGroup.objects.get(pk=coregroup.pk)
