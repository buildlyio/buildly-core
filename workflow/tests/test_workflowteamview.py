import json

from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from workflow.models import (WorkflowTeam, ROLE_ORGANIZATION_ADMIN,
                             ROLE_WORKFLOW_ADMIN, ROLE_WORKFLOW_TEAM,
                             ROLE_VIEW_ONLY)

from ..views import WorkflowTeamViewSet


class WorkflowTeamListViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.CoreUser(
            user=user_ringo, organization=factories.Organization())
        self.wflvl1 = factories.WorkflowLevel1(
            organization=tola_user_ringo.organization)
        factories.WorkflowTeam(workflow_user=tola_user_ringo,
                               workflowlevel1=self.wflvl1,
                               role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_list_workflowteam_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_superuser_and_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)

        # Create a workflow team having a diff partner org
        factories.WorkflowTeam(workflow_user=self.core_user,
                               workflowlevel1=wflvl1)

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_org_admin_diff_user_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        # Create a user belonging to other Project in other Org
        another_org = factories.Organization(name='Another Org')
        user_george = factories.User(first_name='George', last_name='Harrison')
        tola_user_george = factories.CoreUser(
            user=user_george, organization=another_org)
        wflvl1_other = factories.WorkflowLevel1(organization=another_org)
        factories.WorkflowTeam(workflow_user=tola_user_george,
                               workflowlevel1=wflvl1_other)

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_workflowteam_org_admin_diff_user_same_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        # Create a user belonging to other Project in same Org
        user_george = factories.User(first_name='George', last_name='Harrison')
        core_user_george = factories.CoreUser(
            user=user_george, organization=self.core_user.organization)
        wflvl1_other = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        factories.WorkflowTeam(workflow_user=core_user_george,
                               workflowlevel1=wflvl1_other)

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_program_admin(self):
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_program_team(self):
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_view_only(self):
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))

        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_workflowteam_normaluser(self):
        request_get = self.factory.get('/workflowteam/')
        request_get.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_list_workflowteam_anonymoususer(self):
        request_get = self.factory.get('/workflowteam/')
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request_get)
        self.assertEqual(response.status_code, 403)


class WorkflowTeamCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)

    def test_create_workflowteam_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        role = factories.Group(name=ROLE_WORKFLOW_ADMIN)
        data = {
            'role': role.pk,
            'workflow_user': self.core_user.pk,
            'workflowlevel1': self.wflvl1.pk,
        }

        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.core_user,
            role=role,
        )

    def test_create_workflowteam_program_admin(self):
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        role = factories.Group(name=ROLE_WORKFLOW_TEAM)
        data = {
            'role': role.pk,
            'workflow_user': self.core_user.pk,
            'workflowlevel1': self.wflvl1.pk,
        }

        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.core_user,
            role=role,
        )

    def test_create_workflowteam_program_admin_json(self):
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        role = factories.Group(name=ROLE_WORKFLOW_TEAM)
        data = {
            'role': role.pk,
            'workflow_user': self.core_user.pk,
            'workflowlevel1': self.wflvl1.pk,
        }

        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        WorkflowTeam.objects.get(
            workflowlevel1=self.wflvl1,
            workflow_user=self.core_user,
            role=role,
        )

    def test_create_workflowteam_other_user(self):
        role_without_benefits = ROLE_WORKFLOW_TEAM
        WorkflowTeam.objects.create(
            workflow_user=self.core_user, workflowlevel1=self.wflvl1,
            role=factories.Group(name=role_without_benefits))

        role = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        data = {
            'role': role.pk,
            'workflow_user': self.core_user.pk,
            'workflowlevel1': self.wflvl1.id,
        }

        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 403)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, workflowlevel1=self.wflvl1,
            workflow_user=self.core_user,
            role=role,
        )


class WorkflowTeamUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.CoreUser(
            user=user_ringo, organization=self.core_user.organization)
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        self.workflowteam = factories.WorkflowTeam(
            workflow_user=tola_user_ringo,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_update_unexisting_workflowteam(self):
        data = {'status': 'active'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_workflowteam_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        data = {'status': 'active'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        status_updated = WorkflowTeam.objects.\
            values_list('status', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(status_updated, 'active')

    def test_update_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        data = {'status': 'active'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        status_updated = WorkflowTeam.objects.\
            values_list('status', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(status_updated, 'active')

    def test_update_workflowteam_program_admin(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        data = {'status': 'active'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        status_updated = WorkflowTeam.objects.\
            values_list('status', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(status_updated, 'active')

    def test_update_workflowteam_program_admin_json(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        data = {'status': 'active'}
        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 200)

        status_updated = WorkflowTeam.objects.\
            values_list('status', flat=True).get(pk=self.workflowteam.pk)
        self.assertEqual(status_updated, 'active')

    def test_update_workflowteam_other_user(self):
        role_without_benefits = ROLE_WORKFLOW_TEAM
        self.workflowteam.role = factories.Group(name=role_without_benefits)
        self.workflowteam.save()

        data = {'status': 'active'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 403)


class WorkflowTeamDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

        user_ringo = factories.User(first_name='Ringo', last_name='Starr')
        tola_user_ringo = factories.CoreUser(
            user=user_ringo, organization=self.core_user.organization)
        self.wflvl1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        self.workflowteam = factories.WorkflowTeam(
            workflow_user=tola_user_ringo,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_VIEW_ONLY))

    def test_delete_workflowteam_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_program_admin(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_ADMIN))

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 204)

        self.assertRaises(
            WorkflowTeam.DoesNotExist,
            WorkflowTeam.objects.get, pk=self.workflowteam.pk)

    def test_delete_workflowteam_role_without_benefit(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=self.wflvl1,
            role=factories.Group(name=ROLE_WORKFLOW_TEAM))

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.workflowteam.pk)
        self.assertEqual(response.status_code, 403)
        WorkflowTeam.objects.get(pk=self.workflowteam.pk)


class WorkflowTeamFilterViewTest(TestCase):
    def setUp(self):
        self.core_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_filter_workflowteam_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        another_org = factories.Organization(name='Another Org')
        wkflvl1_1 = factories.WorkflowLevel1(
            organization=self.core_user.organization)
        wkflvl1_2 = factories.WorkflowLevel1(
            organization=another_org)
        workflowteam1 = factories.WorkflowTeam(workflow_user=self.core_user,
                                               status='active',
                                               workflowlevel1=wkflvl1_1)
        factories.WorkflowTeam(workflow_user=self.core_user,
                               status='disabled',
                               workflowlevel1=wkflvl1_2)

        request = self.factory.get(
            '/workflowteam/?workflowlevel1__organization__id=%s' %
            self.core_user.organization.pk)
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], str(workflowteam1.status))

    def test_filter_workflowteam_nested_models(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        wkflvl1 = factories.WorkflowLevel1(
            name='Test Workflow',
            organization=self.core_user.organization)
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            workflowlevel1=wkflvl1)

        request = self.factory.get('/workflowteam/?nested_models=1')
        request.user = self.core_user.user
        view = WorkflowTeamViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        wfl1 = response.data[0]['workflowlevel1']
        self.assertEqual(wfl1['name'], 'Test Workflow')
