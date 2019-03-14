import json
import re
from unittest.mock import patch, PropertyMock

from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse
from workflow.models import (WorkflowLevel2, WorkflowTeam,
                             ROLE_VIEW_ONLY, ROLE_ORGANIZATION_ADMIN,
                             ROLE_WORKFLOW_ADMIN, ROLE_WORKFLOW_TEAM)

from ..views import WorkflowLevel2ViewSet


class WorkflowLevel2ListViewsTest(TestCase):
    def setUp(self):
        factories.WorkflowLevel2.create_batch(2)
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_list_workflowlevel2_superuser(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        request.user = factories.User.build(is_superuser=True,
                                            is_staff=True)
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowlevel2_org_admin(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1()
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1)
        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        wflvl1.organization = self.core_user.organization
        wflvl1.save()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2_program_admin(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2_program_team(self):
        request = self.factory.get(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2_view_only(self):
        request = self.factory.get('/api/workflowlevel2/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    @patch('workflow.views.DefaultCursorPagination.page_size',
           new_callable=PropertyMock)
    def test_list_workflowlevel2_pagination(self, page_size_mock):
        ''' For page_size 1 and pagination true, list wfl3 endpoint should
         return 1 wfl2 for each page'''
        # set page_size =1
        page_size_mock.return_value = 1
        wfl1_1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        wfl2_1 = factories.WorkflowLevel2(name='1. wfl2',
                                          workflowlevel1=wfl1_1)
        wfl2_2 = factories.WorkflowLevel2(name='2. wfl2',
                                          workflowlevel1=wfl1_1)

        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.get('?paginate=true')
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)

        # page_size = 1, so it should return just one wfl1
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], wfl2_1.name)

        m = re.search('=(.*)&', response.data['next'])
        cursor = m.group(1)

        request = self.factory.get('?cursor={}&paginate=true'.format(
            cursor))
        request.user = self.core_user.user
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
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1()
        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_program_admin(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk
                }

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_program_admin_json(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'),
                                    json.dumps(data),
                                    content_type='application/json')
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_program_team(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))

        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Help Syrians')

    def test_create_workflowlevel2_view_only(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))

        data = {'name': 'Help Syrians',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 403)

    def test_create_workflowlevel2_uuid_is_self_generated(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))

        data = {
            'name': 'Save the Children',
            'level2_uuid': '84a9888-4149-11e8-842f-0ed5f89f718b',
            'workflowlevel1': wflvl1.pk}

        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(response.data['level2_uuid'],
                            '84a9888-4149-11e8-842f-0ed5f89f718b')


class WorkflowLevel2UpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_update_unexisting_workflowlevel2(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        data = {'name': 'Community awareness program conducted to plant trees'}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(228,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowlevel2_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1()
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertEquals(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertEquals(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_diff_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.post(reverse('workflowlevel2-list'))
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel2_program_admin(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertEquals(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_program_admin_json(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)),
            json.dumps(data),
            content_type='application/json'
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertEquals(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_program_team(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertEquals(workflowlevel2.name, data['name'])

    def test_update_workflowlevel2_view_only(self):
        request = self.factory.post(reverse('workflowlevel2-list'))
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}

        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(workflowlevel2.pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_workflowlevel2_uuid_is_self_generated(self):
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))

        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk}
        request = self.factory.post(reverse('workflowlevel2-list'), data)
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)
        first_level2_uuid = response.data['level2_uuid']
        data = {'name': 'Community awareness program conducted to plant trees',
                'workflowlevel1': wflvl1.pk,
                'level2_uuid': '84a9888-4149-11e8-842f-0ed5f89f718b'}
        pk = int(response.data['id'])
        request = self.factory.put(
            reverse('workflowlevel2-detail', args=(pk,)), data
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'put': 'update'})
        response = view(request, pk=pk)
        self.assertEqual(response.status_code, 200)

        wflvl2 = WorkflowLevel2.objects.get(pk=response.data['id'])
        self.assertNotEqual(wflvl2.level2_uuid,
                            '84a9888-4149-11e8-842f-0ed5f89f718b')
        self.assertEqual(wflvl2.level2_uuid, first_level2_uuid)


class WorkflowLevel2DeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_delete_workflowlevel2_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        workflowlevel2 = factories.WorkflowLevel2()
        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get, pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get, pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_diff_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_program_admin(self):
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2.DoesNotExist,
            WorkflowLevel2.objects.get, pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_diff_org(self):
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_program_team(self):
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_view_only(self):
        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        workflowlevel2 = factories.WorkflowLevel2(workflowlevel1=wflvl1)

        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=workflowlevel2.pk)

    def test_delete_workflowlevel2_normal_user(self):
        workflowlevel2 = factories.WorkflowLevel2()
        request = self.factory.delete(reverse('workflowlevel2-list'))
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2.objects.get(pk=workflowlevel2.pk)


class WorkflowLevel2FilterViewsTest(TestCase):
    def setUp(self):
        factories.Organization(id=1)
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_filter_workflowlevel2_wkflvl1_name_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wkflvl1_1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(
            name='Construction Project',
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1_1)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1_2)
        wkflvl2 = factories.WorkflowLevel2(workflowlevel1=wkflvl1_1)
        factories.WorkflowLevel2(
            name='Develop brief survey', workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '{}?workflowlevel1__name={}'.format(reverse('workflowlevel2-list'),
                                                wkflvl1_1.name)
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wkflvl2.name)

    def test_filter_workflowlevel2_wkflvl1_id_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wkflvl1_1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1_1)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1_2)
        wkflvl2 = factories.WorkflowLevel2(workflowlevel1=wkflvl1_1)
        factories.WorkflowLevel2(
            name='Develop brief survey', workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '{}?workflowlevel1__id={}'.format(reverse('workflowlevel2-list'),
                                                wkflvl1_1.pk)
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wkflvl2.name)

    def test_filter_workflowlevel2_level2_uuid_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wkflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1)
        wkflvl2 = factories.WorkflowLevel2(
            level2_uuid=111, workflowlevel1=wkflvl1)
        factories.WorkflowLevel2(
            name='Develop brief survey', level2_uuid=222,
            workflowlevel1=wkflvl1)

        request = self.factory.get(
            '{}?level2_uuid={}'.format(reverse('workflowlevel2-list'),
                                       wkflvl2.level2_uuid)
        )
        request.user = self.core_user.user
        view = WorkflowLevel2ViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], wkflvl2.name)
