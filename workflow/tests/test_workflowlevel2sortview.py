import uuid

from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from core.models import (
    PERMISSIONS_ORG_ADMIN,
    PERMISSIONS_VIEW_ONLY,
    PERMISSIONS_WORKFLOW_ADMIN,
    PERMISSIONS_WORKFLOW_TEAM,
)
from workflow.models import WorkflowLevel2Sort

from ..views import WorkflowLevel2SortViewSet


class WorkflowLevel2SortListViewsTest(TestCase):
    def setUp(self):
        self.not_default_org = factories.Organization.create(name='Some Org')
        wfl1_not_default_org = factories.WorkflowLevel1.create(
            organization=self.not_default_org
        )
        factories.WorkflowLevel2Sort.create_batch(
            2, workflowlevel1=wfl1_not_default_org
        )
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_list_workflowlevel2sort_superuser(self):
        """
        list view should return all objs to super users
        """
        request = self.factory.get('/workflowlevel2sort/')
        request.user = factories.CoreUser.build(is_superuser=True, is_staff=True)
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowlevel2sort_org_admin(self):
        """
        list view should return only objs of an org to org admins
        """
        request = self.factory.get('/workflowlevel2sort/')
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(organization=self.not_default_org)
        factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_workflowlevel2sort_program_admin(self):
        """
        list view should return only objs associated with programs that
        program admins have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_admin = factories.CoreGroup(
            name='WF Admin',
            permissions=PERMISSIONS_WORKFLOW_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_admin)
        wflvl1.core_groups.add(group_wf_admin)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_workflowlevel2sort_program_team(self):
        """
        list view should return only objs associated with programs that
        program members have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF Team',
            permissions=PERMISSIONS_WORKFLOW_TEAM,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_workflowlevel2sort_view_only(self):
        """
        list view should return only objs associated with programs that
        program view only users have access to
        """
        request = self.factory.get('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        group_wf_team = factories.CoreGroup(
            name='WF View Only',
            permissions=PERMISSIONS_VIEW_ONLY,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_wf_team)
        wflvl1.core_groups.add(group_wf_team)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)


class WorkflowLevel2SortCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_create_workflowlevel2_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1()

        data = {'workflowlevel2_pk': uuid.uuid4(), 'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['workflowlevel2_pk'], str(data['workflowlevel2_pk'])
        )

    def test_create_workflowlevel2sort_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)

        data = {'workflowlevel2_pk': uuid.uuid4(), 'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['workflowlevel2_pk'], str(data['workflowlevel2_pk'])
        )


class WorkflowLevel2SortUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_update_unexisting_workflowlevel2sort(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        data = {'workflowlevel2_pk': 1}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowlevel2sort_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1()
        workflowlevel2sort = factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        data = {'workflowlevel2_pk': uuid.uuid4(), 'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})

        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 200)

        workflowlevel2sort = WorkflowLevel2Sort.objects.get(pk=response.data['id'])
        self.assertEqual(
            str(workflowlevel2sort.workflowlevel2_pk), str(data['workflowlevel2_pk'])
        )

    def test_update_workflowlevel2sort_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2sort = factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        data = {'workflowlevel2_pk': uuid.uuid4(), 'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=workflowlevel2sort.pk)

        self.assertEqual(response.status_code, 200)

        workflowlevel2sort = WorkflowLevel2Sort.objects.get(pk=response.data['id'])
        self.assertEqual(
            workflowlevel2sort.workflowlevel2_pk, data['workflowlevel2_pk']
        )

    def test_update_workflowlevel2sort_diff_org_normal_user(self):
        request = self.factory.post('/workflowlevel2sort/')
        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2sort = factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        data = {'workflowlevel2_pk': uuid.uuid4(), 'workflowlevel1': wflvl1.pk}

        request = self.factory.post('/workflowlevel2sort/', data)
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'post': 'update'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 403)


class WorkflowLevel2SortDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        factories.Group()

    def test_delete_workflowlevel2sort_superuser(self):
        self.core_user.is_staff = True
        self.core_user.is_superuser = True
        self.core_user.save()

        workflowlevel2sort = factories.WorkflowLevel2Sort()
        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2Sort.DoesNotExist,
            WorkflowLevel2Sort.objects.get,
            pk=workflowlevel2sort.pk,
        )

    def test_delete_workflowlevel2sort_normal_user(self):
        wflvl1 = factories.WorkflowLevel1(organization=self.core_user.organization)
        workflowlevel2sort = factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 204)
        self.assertRaises(
            WorkflowLevel2Sort.DoesNotExist,
            WorkflowLevel2Sort.objects.get,
            pk=workflowlevel2sort.pk,
        )

    def test_delete_workflowlevel2sort_diff_org_normal_user(self):
        group_org_admin = factories.CoreGroup(
            name='Org Admin',
            is_org_level=True,
            permissions=PERMISSIONS_ORG_ADMIN,
            organization=self.core_user.organization,
        )
        self.core_user.core_groups.add(group_org_admin)

        another_org = factories.Organization(name='Another Org')
        wflvl1 = factories.WorkflowLevel1(organization=another_org)
        workflowlevel2sort = factories.WorkflowLevel2Sort(workflowlevel1=wflvl1)

        request = self.factory.delete('/workflowlevel2sort/')
        request.user = self.core_user
        view = WorkflowLevel2SortViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=workflowlevel2sort.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowLevel2Sort.objects.get(pk=workflowlevel2sort.pk)
