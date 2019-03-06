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

    def test_coreuser_views_permissions_org_member(self, request_factory, org_member):
        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 403

        request = request_factory.post(reverse('coregroup-list'))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 403

        request = request_factory.get(reverse('coregroup-detail', args=(1,)))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.put(reverse('coregroup-detail', args=(1,)))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.patch(reverse('coregroup-detail', args=(1,)))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        assert response.status_code == 403

        request = request_factory.delete(reverse('coregroup-detail', args=(1,)))
        request.user = org_member.user
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        assert response.status_code == 403

    def test_coreuser_views_permissions_different_org_admin(self, request_factory, org, group_org_admin):
        coreuser = factories.CoreUser.create(organization=factories.Organization(name='Another Org'))
        coreuser.user.groups.add(group_org_admin)

        # TODO: this should work after permissions refactoring
        # request = request_factory.get(reverse('coregroup-detail', args=(org.pk,)))
        # request.user = coreuser.user
        # response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=org.pk)
        # assert response.status_code == 403
        #
        # request = request_factory.put(reverse('coregroup-detail', args=(org.pk,)))
        # request.user = coreuser.user
        # response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=org.pk)
        # assert response.status_code == 403
        #
        # request = request_factory.patch(reverse('coregroup-detail', args=(org.pk,)))
        # request.user = coreuser.user
        # response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=org.pk)
        # assert response.status_code == 403
        #
        # request = request_factory.delete(reverse('coregroup-detail', args=(1,)))
        # request.user = coreuser.user
        # response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        # assert response.status_code == 403


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
            'role': wfm.ROLE_PROGRAM_ADMIN,
            'workflowlevel1': wfl1.pk,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(group__name='New Group')
        assert coregroup.id == response.data['id']
        assert coregroup.organization == org_admin.organization
        assert coregroup.role == wfm.ROLE_PROGRAM_ADMIN

    def test_coregroup_create_with_permissions(self, request_factory, org_admin):
        permissions = Permission.objects.values_list('id', flat=True)[:2]
        data = {
            'group': {'name': 'New Group', 'permissions': permissions},
            'role': wfm.ROLE_PROGRAM_ADMIN,
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
        permissions = Permission.objects.values_list('id', flat=True)[:3]
        coregroup = factories.CoreGroup.create()
        coregroup.group.permissions.set(permissions[:2])  # 1st and 2nd permissions

        data = {
            'group': {'name': 'Updated Name', 'permissions': permissions[1:]},  # 2nd and 3rd permissions
        }

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)), data, format='json')
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        coregroup_upd = wfm.CoreGroup.objects.get(pk=coregroup.pk)
        assert coregroup_upd.group.name == 'Updated Name'
        assert set(permissions[1:]) == set(coregroup_upd.group.permissions.values_list('id', flat=True))


@pytest.mark.django_db()
class TestCoreUserListView:

    def test_coregroup_list(self, request_factory, org_admin):
        # we have already 2 core groups for organization created in fixture
        another_org = factories.Organization.create()  # 2 core groups are created here for another org

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin.user
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db()
class TestCoreUserDetailView:

    def test_coregroup_detail(self, request_factory, org_member):
        pass


@pytest.mark.django_db()
class TestCoreUserDeleteView:

    def test_coregroup_detete(self, request_factory, org_member):
        pass
