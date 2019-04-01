import pytest
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
        wfl1 = factories.WorkflowLevel1.create(organization=org)
        coregroup = factories.CoreGroup.create(workflowlevel1=wfl1)

        # create admin of another organization
        wfl1_another = factories.WorkflowLevel1.create(organization=factories.Organization(name='Another Org'))
        coreuser = factories.CoreUser.create(workflowlevel1=wfl1_another)
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
        assert coregroup.organization is None
        assert coregroup.permissions == 4  # check default permissions

    def test_coregroup_create_with_workfllow1(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        data = {
            'name': 'New Group',
            'workflowlevel1': wfl1.pk,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(name='New Group')
        assert coregroup.workflowlevel1 == wfl1
        assert coregroup.workflowlevel2 is None

    def test_coregroup_create_with_workfllow2(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        wfl2 = factories.WorkflowLevel2.create(workflowlevel1=wfl1)
        data = {
            'name': 'New Group',
            'workflowlevel2': wfl2.pk,
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = wfm.CoreGroup.objects.get(name='New Group')
        assert coregroup.workflowlevel1 is None
        assert coregroup.workflowlevel2 == wfl2


@pytest.mark.django_db()
class TestCoreGroupUpdateView:

    def test_coregroup_update(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        coregroup = factories.CoreGroup.create(name='Program Admin', workflowlevel1=wfl1)

        data = {
            'name': 'Admin of something else',
            'permissions': 9,
        }

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        coregroup_upd = wfm.CoreGroup.objects.get(pk=coregroup.pk)
        assert coregroup_upd.name == 'Admin of something else'
        assert coregroup_upd.permissions == 9


@pytest.mark.django_db()
class TestCoreGroupListView:

    def test_coregroup_list(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        wfl1_another_org = factories.WorkflowLevel1.create(organization=factories.Organization(name='Another org'))
        factories.CoreGroup.create(name='Group 1', workflowlevel1=wfl1)
        factories.CoreGroup.create(name='Group 2', workflowlevel1=wfl1)
        factories.CoreGroup.create(name='Group 3', workflowlevel1=wfl1_another_org)

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 2


@pytest.mark.django_db()
class TestCoreGroupDetailView:

    def test_coregroup_detail(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        coregroup = factories.CoreGroup.create(workflowlevel1=wfl1)

        request = request_factory.get(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        assert response.data['workflowlevel1'] == wfl1.id


@pytest.mark.django_db()
class TestCoreGroupDeleteView:

    def test_coregroup_delete(self, request_factory, org_admin):
        wfl1 = factories.WorkflowLevel1.create(organization=org_admin.organization)
        coregroup = factories.CoreGroup.create(workflowlevel1=wfl1)

        request = request_factory.delete(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=coregroup.pk)
        assert response.status_code == 204

        with pytest.raises(wfm.CoreGroup.DoesNotExist):
            wfm.CoreGroup.objects.get(pk=coregroup.pk)
