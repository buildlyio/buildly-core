import json
import re
from unittest.mock import patch, PropertyMock

from django.test import TestCase
import factories
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from core.models import (
    PERMISSIONS_ORG_ADMIN,
    PERMISSIONS_WORKFLOW_ADMIN,
    PERMISSIONS_WORKFLOW_TEAM,
    PERMISSIONS_VIEW_ONLY,
)
from workflow.models import WorkflowLevel1

from ..views import WorkflowLevel1ViewSet


class WorkflowLevel1ListViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_list_workflowlevel1_superuser(self):
        wflvl1 = factories.WorkflowLevel1()

        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_list_workflowlevel1_superuser_and_org_admin(self):
        wflvl1 = factories.WorkflowLevel1()
        wflvl2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_list_workflowlevel1_org_admin(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wflvl2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_list_workflowlevel1_program_admin(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wflvl2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wfl1_admin = factories.CoreGroup(
            name='Workflow Admin', permissions=PERMISSIONS_WORKFLOW_ADMIN
        )
        wflvl1.core_groups.add(group_wfl1_admin)
        self.core_user.core_groups.add(group_wfl1_admin)

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_list_filter_workflowlevel1_program_admin(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wflvl1_2 = factories.WorkflowLevel1(
            name='Population Health Initiative',
            organization=self.core_user.organization,
        )

        group_wfl1_admin = factories.CoreGroup(
            name='Workflow Admin', permissions=PERMISSIONS_WORKFLOW_ADMIN
        )
        wflvl1.core_groups.add(group_wfl1_admin)
        wflvl1_2.core_groups.add(group_wfl1_admin)
        self.core_user.core_groups.add(group_wfl1_admin)

        request = self.factory.get(
            '{}?name={}'.format(reverse('workflowlevel1-list'), wflvl1.name)
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)
        self.assertNotEqual(response.data[0]['name'], wflvl1_2.name)

    def test_list_workflowlevel1_program_team(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_list_workflowlevel1_normal_user_same_org(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request = self.factory.get(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch(
        'workflow.pagination.DefaultCursorPagination.page_size',
        new_callable=PropertyMock,
    )
    def test_list_workflowlevel1_pagination(self, page_size_mock):
        """ For page_size 1 and pagination true, list wfl1 endpoint should
         return 1 wfl1 for each page"""
        # set page_size =1
        page_size_mock.return_value = 1
        wfl1_1 = factories.WorkflowLevel1(
            name='1. wfl', organization=self.core_user.organization
        )
        wfl1_2 = factories.WorkflowLevel1(
            name='2. wfl', organization=self.core_user.organization
        )
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.get('?paginate=true')
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # page_size = 1, so it should return just one wfl1
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wfl1_1.name)

        m = re.search('=(.*)&', response.data['next'])
        cursor = m.group(1)

        request = self.factory.get('?cursor={}&paginate=true'.format(cursor))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wfl1_2.name)


class WorkflowLevel1CreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_create_workflowlevel1_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        data = {
            'name': 'Save the Children',
            'organization': self.core_user.organization.pk,
        }
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Save the Children')

        wflvl1 = WorkflowLevel1.objects.get(pk=response.data['id'])
        self.assertEqual(wflvl1.organization, self.core_user.organization)
        self.assertEqual(wflvl1.user_access.all().count(), 1)
        self.assertEqual(wflvl1.user_access.first(), self.core_user)

    def test_create_workflowlevel1_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        data = {'name': 'Save the Children'}
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Save the Children')

        wflvl1 = WorkflowLevel1.objects.get(pk=response.data['id'])
        self.assertEqual(wflvl1.organization, self.core_user.organization)
        self.assertEqual(wflvl1.user_access.all().count(), 1)
        self.assertEqual(wflvl1.user_access.first(), self.core_user)

    def test_create_workflowlevel1_normal_user(self):
        data = {'name': 'Save the Children'}
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user

        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 403)

    def test_create_workflowlevel1_uuid_is_self_generated(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)
        data = {
            'name': 'Save the Children',
            'level1_uuid': '75e4c912-4149-11e8-842f-0ed5f89f718b',
        }
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(
            response.data['level1_uuid'], '75e4c912-4149-11e8-842f-0ed5f89f718b'
        )


class WorkflowLevel1UpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_update_unexisting_workflowlevel1(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        data = {'salary': '10'}
        request = self.factory.put(reverse('workflowlevel1-detail', args=(288,)), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowlevel1_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        wflvl1 = factories.WorkflowLevel1()
        data = {'name': 'Save the Lennons'}
        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wflvl1.pk,)), data
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 200)

        wflvl1 = WorkflowLevel1.objects.get(pk=response.data['id'])
        self.assertEqual(wflvl1.name, data['name'])

    def test_update_workflowlevel1_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        data = {'name': 'Save the Lennons'}
        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wflvl1.pk,)), data
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 200)

        wflvl1 = WorkflowLevel1.objects.get(pk=response.data['id'])
        self.assertEqual(wflvl1.name, data['name'])

    def test_update_workflowlevel1_different_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(
            organization=factories.Organization(name='Other Org')
        )
        data = {'name': 'Save the Lennons'}
        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wflvl1.pk,)), data
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel1_program_admin(self):
        wfl1 = factories.WorkflowLevel1.create(
            name='Save the Children', organization=self.core_user.organization
        )

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wfl1.core_groups.add(group_wf_admin)

        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wfl1.pk,)),
            {'name': 'Save the Lennons'},
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wfl1.pk)
        # WFL1 admin doesn't have permissions to update this WFL1 itself
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel1_program_admin_json(self):
        wfl1 = factories.WorkflowLevel1.create(
            name='Save the Children', organization=self.core_user.organization
        )

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wfl1.core_groups.add(group_wf_admin)

        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wfl1.pk,)),
            json.dumps({'name': 'Save the Lennons'}),
            content_type='application/json',
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wfl1.pk)
        # WFL1 admin doesn't have permissions to update this WFL1 itself
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel1_program_team(self):
        wflvl1 = factories.WorkflowLevel1()
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wflvl1.pk,)),
            {'name': 'Save the Lennons'},
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wflvl1.pk)
        # WFL1 admin doesn't have permissions to update this WFL1 itself
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel1_same_org_different_program_team(self):
        wflvl1_other = factories.WorkflowLevel1()
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1_other.core_groups.add(group_wf_team)

        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        data = {'name': 'Save the Lennons'}
        request = self.factory.put(
            reverse('workflowlevel1-detail', args=(wflvl1.pk,)), data
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'put': 'update'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 403)


class WorkflowLevel1DeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_delete_workflowlevel1_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        wflvl1 = factories.WorkflowLevel1()
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel1.DoesNotExist, WorkflowLevel1.objects.get, pk=wflvl1.pk
        )

    def test_delete_workflowlevel1_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel1.DoesNotExist, WorkflowLevel1.objects.get, pk=wflvl1.pk
        )

    def test_delete_workflowlevel1_different_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        org_other = factories.Organization(name='Other Org')
        wflvl1 = factories.WorkflowLevel1(organization=org_other)
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowLevel1.objects.get(pk=wflvl1.pk)

    def test_delete_workflowlevel1_program_admin(self):
        wfl1 = factories.WorkflowLevel1(name='Save the Children')

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wfl1.core_groups.add(group_wf_admin)

        # Only org admin can delete the workflow level 1
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wfl1.pk)
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(WorkflowLevel1.objects.filter(pk=wfl1.pk).first())

    def test_delete_workflowlevel1_different_org(self):
        group_other = factories.Group(name='other')
        self.core_user.groups.add(group_other)

        wflvl1 = factories.WorkflowLevel1()
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowLevel1.objects.get(pk=wflvl1.pk)

    def test_delete_workflowlevel1_normal_user(self):
        wflvl1 = factories.WorkflowLevel1()
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=wflvl1.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowLevel1.objects.get(pk=wflvl1.pk)

    def test_delete_workflowlevel1_program_admin_just_one(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        # Create a program
        data = {'name': 'Save the Pandas'}
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        first_program_id = response.data['id']

        # Create another program
        data = {'name': 'Save the Children'}
        request = self.factory.post(reverse('workflowlevel1-list'), data)
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'post': 'create'})
        response = view(request)
        second_program_id = response.data['id']

        # Delete only the latter program
        request = self.factory.delete(reverse('workflowlevel1-list'))
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=second_program_id)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel1.DoesNotExist,
            WorkflowLevel1.objects.get,
            pk=second_program_id,
        )
        WorkflowLevel1.objects.get(pk=first_program_id)


class WorkflowLevel1FilterViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_filter_workflowlevel1_superuser(self):
        wflvl1 = factories.WorkflowLevel1()
        factories.WorkflowLevel1(name='Population Health Initiative')

        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.get(
            '{}?name={}'.format(reverse('workflowlevel1-list'), wflvl1.name)
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)

    def test_filter_workflowlevel1_org_admin(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        factories.WorkflowLevel1(
            name='Population Health Initiative',
            organization=self.core_user.organization,
        )
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.get(
            '{}?name={}'.format(reverse('workflowlevel1-list'), wflvl1.name)
        )
        request.user = self.core_user
        view = WorkflowLevel1ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wflvl1.name)
