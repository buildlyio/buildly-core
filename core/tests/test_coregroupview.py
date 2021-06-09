import pytest
from rest_framework.reverse import reverse

import factories
from core.tests.fixtures import org, org_admin, org_member, reset_password_request, TEST_USER_DATA
from core.models import CoreGroup
from core.views import CoreGroupViewSet


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
        assert response.status_code == 200

        request = request_factory.post(reverse('coregroup-list'))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 403

        request = request_factory.get(reverse('coregroup-detail', args=(1000,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=1000)
        assert response.status_code == 404  # it's allowed but doesn't exist

        request = request_factory.put(reverse('coregroup-detail', args=(1000,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=1000)
        assert response.status_code == 404  # it's allowed but wf1 is from different org

        request = request_factory.patch(reverse('coregroup-detail', args=(1000,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=1000)
        assert response.status_code == 404  # it's allowed but wf1 is from different org

        request = request_factory.delete(reverse('coregroup-detail', args=(1000,)))
        request.user = org_member
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1000)
        assert response.status_code == 404  # first checks if exists, then checks object permissions

    def test_coregroup_views_permissions_org_admin(self, request_factory, org_admin):
        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200

        request = request_factory.post(reverse('coregroup-list'), {'organization': org_admin.organization.pk},
                                       format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

        request = request_factory.get(reverse('coregroup-detail', args=(1,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=1)
        assert response.status_code == 404

        request = request_factory.put(reverse('coregroup-detail', args=(1,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=1)
        assert response.status_code == 404

        request = request_factory.patch(reverse('coregroup-detail', args=(1,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'patch': 'partial_update'})(request, pk=1)
        assert response.status_code == 404

        request = request_factory.delete(reverse('coregroup-detail', args=(1,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=1)
        assert response.status_code == 404


@pytest.mark.django_db()
class TestCoreGroupCreateView:

    def test_coregroup_create_fail_missing_required_fields(self, request_factory, org_admin):
        request = request_factory.post(reverse('coregroup-list'), {'organization': org_admin.organization.pk},
                                       format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_coregroup_create_min(self, request_factory, org_admin):
        data = {'name': 'New Group', 'organization': org_admin.organization.pk}
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = CoreGroup.objects.get(name='New Group')
        assert coregroup.permissions == 4  # check default permissions
        assert coregroup.organization == org_admin.organization

    def test_coregroup_create_fail(self, request_factory, org_admin):
        data = {
            'name': 'New Group',
            'permissions': 9,
            'organization': org_admin.organization.pk
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_coregroup_create_fail_again(self, request_factory, org_admin):
        data = {
            'name': 'New Group',
            'permissions': '1001',
            'organization': org_admin.organization.pk
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 400

    def test_coregroup_create(self, request_factory, org_admin):
        data = {
            'name': 'New Group',
            'permissions': {'create': True, 'read': False, 'update': False, 'delete': True},
            'organization': org_admin.organization.pk
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = CoreGroup.objects.get(name='New Group')
        assert coregroup.permissions == 9
        assert coregroup.organization == org_admin.organization

    def test_coregroup_create_int(self, request_factory, org_admin):
        # int values should also work as well as boolean
        data = {
            'name': 'New Group',
            'permissions': {'create': 1, 'read': 0, 'update': 0, 'delete': 1},
            'organization': org_admin.organization.pk
        }
        request = request_factory.post(reverse('coregroup-list'), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'post': 'create'})(request)
        assert response.status_code == 201
        coregroup = CoreGroup.objects.get(name='New Group')
        assert coregroup.permissions == 9
        assert coregroup.organization == org_admin.organization


@pytest.mark.django_db()
class TestCoreGroupUpdateView:

    def test_coregroup_update_fail(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(name='Program Admin', organization=org_admin.organization)

        data = {
            'name': 'Admin of something else',
            'permissions': 9,
        }

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 400

    def test_coregroup_update(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(name='Program Admin', organization=org_admin.organization)

        data = {
            'name': 'Admin of something else',
            'permissions': {'create': True, 'read': False, 'update': False, 'delete': True},
        }

        request = request_factory.put(reverse('coregroup-detail', args=(coregroup.pk,)), data, format='json')
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'put': 'update'})(request, pk=coregroup.pk)
        assert response.status_code == 200
        coregroup_upd = CoreGroup.objects.get(pk=coregroup.pk)
        assert coregroup_upd.name == 'Admin of something else'
        assert coregroup_upd.permissions == 9


@pytest.mark.django_db()
class TestCoreGroupListView:

    def test_coregroup_list(self, request_factory, org_admin):
        factories.CoreGroup.create(name='Group 1', organization=org_admin.organization)
        factories.CoreGroup.create(name='Group 2', organization=org_admin.organization)

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 5  # Admins, Users groups and its own group + 2 new

    def test_coregroup_list_another_org(self, request_factory, org_admin):
        another_org = factories.Organization(name='Another org')
        factories.CoreGroup.create(name='Group 1', organization=org_admin.organization)
        factories.CoreGroup.create(name='Group 2', organization=another_org)

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 4  # Admins, Users groups and its own group + 1 new

    def test_coregroup_list_global(self, request_factory, org_admin):
        factories.CoreGroup.create(name='Group 1', organization=org_admin.organization)
        factories.CoreGroup.create(name='Group Global', organization=None, is_global=True)

        request = request_factory.get(reverse('coregroup-list'))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'list'})(request)
        assert response.status_code == 200
        assert len(response.data) == 4  # Admins, Users groups and its own group + 1 new


@pytest.mark.django_db()
class TestCoreGroupDetailView:

    def test_coregroup_detail(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(organization=org_admin.organization)

        request = request_factory.get(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=coregroup.pk)
        assert response.status_code == 200

    def test_coregroup_detail_another_org(self, request_factory, org_admin):
        another_org = factories.Organization(name='Another org')
        coregroup = factories.CoreGroup.create(organization=another_org)

        request = request_factory.get(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'get': 'retrieve'})(request, pk=coregroup.pk)
        assert response.status_code == 403


@pytest.mark.django_db()
class TestCoreGroupDeleteView:

    def test_coregroup_delete(self, request_factory, org_admin):
        coregroup = factories.CoreGroup.create(organization=org_admin.organization)

        request = request_factory.delete(reverse('coregroup-detail', args=(coregroup.pk,)))
        request.user = org_admin
        response = CoreGroupViewSet.as_view({'delete': 'destroy'})(request, pk=coregroup.pk)
        assert response.status_code == 204

        with pytest.raises(CoreGroup.DoesNotExist):
            CoreGroup.objects.get(pk=coregroup.pk)
