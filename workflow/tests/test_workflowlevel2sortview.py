from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse
from workflow.models import (WorkflowLevel2Sort, WorkflowTeam,
                             ROLE_ORGANIZATION_ADMIN, ROLE_PROGRAM_ADMIN,
                             ROLE_PROGRAM_TEAM, ROLE_VIEW_ONLY)

from ..views import WorkflowLevel2SortViewSet


class WorkflowLevel2SortListViewsTest(TestCase):
    def setUp(self):
        factories.WorkflowLevel2Sort.create_batch(2)
        self.factory = APIRequestFactory()
        self.tola_user = factories.CoreUser()

    def test_list_workflowlevel2sort_superuser(self):
        """
        list view should return all objs to super users
        """
        request = self.factory.get('/workflowlevel2sort/')
        request.user = factories.User.build(is_superuser=True,
                                            is_staff=True)
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowlevel2sort_org_admin(self):
        """
        list view should return only objs of an org to org admins
        """
        request = self.factory.get('/workflowlevel2sort/')
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1()
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            workflowlevel1=wflvl1)
        factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        wflvl1.organization = self.tola_user.organization
        wflvl1.save()
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2sort_program_admin(self):
        """
        list view should return only objs associated with programs that
        program admins have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2sort_program_team(self):
        """
        list view should return only objs associated with programs that
        program members have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowlevel2sort_view_only(self):
        """
        list view should return only objs associated with programs that
        program view only users have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            workflowlevel1=wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class WorkflowLevel2SortCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.CoreUser()
        factories.Group()

    def test_create_workflowlevel2_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1()

        data = {'workflowlevel2_id': 1,
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['workflowlevel2_id'], 1)

    def test_create_workflowlevel2sort_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)

        data = {'workflowlevel2_id': 1,
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['workflowlevel2_id'], 1)


class WorkflowLevel2SortUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.CoreUser()
        factories.Group()

    def test_update_unexisting_workflowlevel2sort(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        data = {'workflowlevel2_id': 1}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowlevel2sort_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1()
        workflowlevel2sort = \
            factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        data = {'workflowlevel2_id': 1,
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2sort = WorkflowLevel2Sort.objects.get(
            pk=response.data['id'])
        self.assertEquals(workflowlevel2sort.workflowlevel2_id,
                          data['workflowlevel2_id'])

    def test_update_workflowlevel2sort_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        workflowlevel2sort = factories.WorkflowLevel2Sort(
            workflowlevel1=wflvl1)

        data = {'workflowlevel2_id': 1,
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2sort = WorkflowLevel2Sort.objects.get(
            pk=response.data['id'])
        self.assertEquals(workflowlevel2sort.workflowlevel2_id,
                          data['workflowlevel2_id'])

    def test_update_workflowlevel2sort_diff_org_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2sort = factories.WorkflowLevel2Sort(
            workflowlevel1=wflvl1)

        data = {'workflowlevel2_id': 1,
                'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 403)


class WorkflowLevel2SortDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.tola_user = factories.CoreUser()
        factories.Group()

    def test_delete_workflowlevel2sort_superuser(self):
        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        workflowlevel2sort = factories.WorkflowLevel2Sort()
        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2Sort.DoesNotExist,
            WorkflowLevel2Sort.objects.get, pk=workflowlevel2sort.pk)

    def test_delete_workflowlevel2sort_normal_user(self):
        wflvl1 = factories.WorkflowLevel1(
            organization=self.tola_user.organization)
        workflowlevel2sort = factories.WorkflowLevel2Sort(
            workflowlevel1=wflvl1)

        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2Sort.DoesNotExist,
            WorkflowLevel2Sort.objects.get, pk=workflowlevel2sort.pk)

    def test_delete_workflowlevel2sort_diff_org_normal_user(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2sort = factories.WorkflowLevel2Sort(
            workflowlevel1=wflvl1)

        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.tola_user.user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEquals(response.status_code, 403)
        WorkflowLevel2Sort.objects.get(pk=workflowlevel2sort.pk)
