import json
import uuid
from unittest.mock import patch, PropertyMock

from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse
from core.models import (
    PERMISSIONS_WORKFLOW_ADMIN,
    PERMISSIONS_ORG_ADMIN,
    PERMISSIONS_VIEW_ONLY,
    PERMISSIONS_WORKFLOW_TEAM,
)
from workflow.models import WorkflowLevel2

from ..views import WorkflowLevel2ViewSet


class WorkflowLevel2ListViewsTest(TestCase):
    def setUp(self):
        self.not_default_org = factories.Organization.create(name='Some Org')
        wfl1_not_default_org = factories.WorkflowLevel1.create(
            organization=self.not_default_org
        )
        factories.WorkflowLevel2.create_batch(2, workflowlevel1=wfl1_not_default_org)
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_list_workflowlevel2_superuser(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        request.user = factories.CoreUser.build(is_superuser=True, is_staff=True)
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_list_workflowlevel2_org_admin(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(organization=self.not_default_org)
        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        wflvl1.organization = self.core_user.organization
        wflvl1.save()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_workflowlevel2_program_admin(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_workflowlevel2_program_team(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_workflowlevel2_view_only(self):
        request = self.factory.get('/api/workflowlevel2/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)

    @patch(
        'workflow.pagination.DefaultLimitOffsetPagination.default_limit',
        new_callable=PropertyMock,
    )
    def test_list_workflowlevel2_pagination(self, default_limit_mock):
        """ For default_limit 1 and pagination by default, list wfl2 endpoint should
         return 1 wfl2 for each page"""
        # set default_limit =1
        default_limit_mock.return_value = 1
        wfl1_1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wfl2_1 = factories.WorkflowLevel2(name='1. wfl2', workflowlevel1=wfl1_1)
        wfl2_2 = factories.WorkflowLevel2(name='2. wfl2', workflowlevel1=wfl1_1)

        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.get('')
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # default_limit = 1, so it should return just one wfl2
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wfl2_1.name)

        request = self.factory.get(response.data['next'])
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wfl2_2.name)


class WorkflowLevel2CreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_create_workflowlevel2_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1()
        data = {'name': 'Help Syrians', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        wfltype = factories.WorkflowLevelType()
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        data = {
            'name': 'Help Syrians',
            'workflowlevel1': wflvl1.pk,
            'type': wfltype.uuid,
        }
        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')
        self.assertEqual(response.data['type'], wfltype.uuid)

    def test_create_workflowlevel2_program_admin(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        data = {'name': 'Help Syrians', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_program_admin_json(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        data = {'name': 'Help Syrians', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(
            reverse('workflowlevel2-list'),
            json.dumps(data),
            content_type='application/json',
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_program_team(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {'name': 'Help Syrians', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_view_only(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {'name': 'Help Syrians', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_create_workflowlevel2_uuid_is_self_generated(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {'name': 'Save the Children', 'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(uuid.UUID(response.data['level2_uuid']))


class WorkflowLevel2UpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_update_unexisting_workflowlevel2(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        data = {'name': 'Community awareness program conducted to plant trees'}

        request = self.factory.put(reverse('workflowlevel2-detail', args=(228,)), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowlevel2_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1()
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['level2_uuid'])
        self.assertEqual(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)
        wfltype = factories.WorkflowLevelType()

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
            'type': wfltype.uuid,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['level2_uuid'])
        self.assertEqual(workflowlevel2.name, data['name'])
        self.assertEqual(workflowlevel2.type, wfltype)

    def test_update_workflowlevel2_diff_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel2_program_admin(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['level2_uuid'])
        self.assertEqual(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_program_admin_json(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)),
            json.dumps(data),
            content_type='application/json',
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['level2_uuid'])
        self.assertEqual(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_program_team(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['level2_uuid'])
        self.assertEqual(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_view_only(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(str(workflowlevel2.pk),)), data
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})

        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel2_uuid_is_self_generated(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
        }
        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        first_level2_uuid = response.data['level2_uuid']
        data = {
            'name': 'Community awareness program conducted to plant trees',
            'workflowlevel1': wflvl1.pk,
            'level2_uuid': '84a9888-4149-11e8-842f-0ed5f89f718b',
        }
        pk = first_level2_uuid
        request = self.factory.put(reverse('workflowlevel2-detail', args=(pk,)), data)
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, 400)


class WorkflowLevel2DeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_delete_workflowlevel2_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        workflowlevel2 = factories.WorkflowLevel2()
        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get,
            pk=str(workflowlevel2.pk),
        )

    def test_delete_workflowlevel2_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get,
            pk=str(workflowlevel2.pk),
        )

    def test_delete_workflowlevel2_diff_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=str(workflowlevel2.pk))

    def test_delete_workflowlevel2_program_admin(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)
        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        print('------ response')
        print(response.data)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get,
            pk=str(workflowlevel2.pk),
        )

    def test_delete_workflowlevel2_diff_org(self):
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)
        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=str(workflowlevel2.pk))

    def test_delete_workflowlevel2_program_team(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=str(workflowlevel2.pk))

    def test_delete_workflowlevel2_view_only(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=str(workflowlevel2.pk))

    def test_delete_workflowlevel2_normal_user(self):
        workflowlevel2 = factories.WorkflowLevel2()
        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=str(workflowlevel2.pk))
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=str(workflowlevel2.pk))


class WorkflowLevel2FilterViewsTest(TestCase):
    def setUp(self):
        factories.Organization()
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_filter_workflowlevel2_wkflvl1_name_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wkflvl1_1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(
            name='Construction Project', organization=self.core_user.organization
        )
        wkflvl2 = factories.WorkflowLevel2(workflowlevel1=wkflvl1_1)
        factories.WorkflowLevel2(name='Develop brief survey', workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '{}?workflowlevel1__name={}'.format(
                reverse('workflowlevel2-list'), wkflvl1_1.name
            )
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wkflvl2.name)

    def test_filter_workflowlevel2_wkflvl1_id_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wkflvl1_1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wkflvl2 = factories.WorkflowLevel2(workflowlevel1=wkflvl1_1)
        factories.WorkflowLevel2(name='Develop brief survey', workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '{}?workflowlevel1__id={}'.format(
                reverse('workflowlevel2-list'), wkflvl1_1.pk
            )
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wkflvl2.name)

    def test_filter_workflowlevel2_create_date_range_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wkflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        date1 = '2019-05-01'
        date2 = '2019-05-02'
        date3 = '2019-05-03'

        factories.WorkflowLevel2(workflowlevel1=wkflvl1, create_date=date1)
        level22_uuid = uuid.uuid4()
        wkflvl22 = WorkflowLevel2.objects.create(
            workflowlevel1=wkflvl1, create_date=date2, level2_uuid=level22_uuid
        )
        factories.WorkflowLevel2(workflowlevel1=wkflvl1, create_date=date3)

        request = self.factory.get(
            f'{reverse("workflowlevel2-list")}?create_date_gte={date2}&create_date_lte={date2}'
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['level2_uuid'], str(level22_uuid))

    def test_filter_workflowlevel2_status_org_admin(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wkflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        wfl_status1 = factories.WorkflowLevelStatus(
            name="Started Test Status", short_name="started"
        )
        wfl_status2 = factories.WorkflowLevelStatus(
            name="Finished Test Status", short_name="finished"
        )
        wkflvl2_1 = factories.WorkflowLevel2(
            name='Started brief survey', workflowlevel1=wkflvl1, status=wfl_status1
        )
        wkflvl2_2 = factories.WorkflowLevel2(
            name='Finished brief survey', workflowlevel1=wkflvl1, status=wfl_status2
        )

        # filter by status.uuid
        request = self.factory.get(
            f"{reverse('workflowlevel2-list')}?status__uuid={str(wfl_status1.pk)}"
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wkflvl2_1.name)

        # filter by status.short_name
        request = self.factory.get(
            f"{reverse('workflowlevel2-list')}?status__short_name=finished"
        )
        request.user = self.core_user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wkflvl2_2.name)
