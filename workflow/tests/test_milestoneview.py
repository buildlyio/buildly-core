import json

from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from rest_framework.reverse import reverse
from workflow.models import WorkflowTeam, ROLE_ORGANIZATION_ADMIN, \
    ROLE_PROGRAM_TEAM, ROLE_PROGRAM_ADMIN, ROLE_VIEW_ONLY

from ..views import MilestoneViewSet


class MilestoneListViewsTest(TestCase):
    def setUp(self):
        factories.Milestone.create_batch(2,
            organization=factories.Organization.create(name='Another org')
        )
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_list_milestone_superuser(self):
        request = self.factory.get('/milestone/')
        request.user = factories.User.build(is_superuser=True,
                                            is_staff=True)
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_milestone_org_admin(self):
        request = self.factory.get('/milestone/')
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request.user = self.core_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.core_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_program_admin(self):
        request = self.factory.get('/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))
        request.user = self.core_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.core_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_program_team(self):
        request = self.factory.get('/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))
        request.user = self.core_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.core_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_milestone_view_only(self):
        request = self.factory.get('/milestone/')
        WorkflowTeam.objects.create(
            workflow_user=self.core_user,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        request.user = self.core_user.user
        view = MilestoneViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.Milestone(organization=self.core_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class MilestoneViewTest(TestCase):
    def setUp(self):
        self.user = factories.User(is_superuser=True, is_staff=True)
        factory = APIRequestFactory()
        self.request = factory.post('/milestone/')

    def test_create_milestone(self):
        data = {'name': 'Project Implementation'}
        self.request = APIRequestFactory().post('/milestone/', data)
        self.request.user = self.user
        view = MilestoneViewSet.as_view({'post': 'create'})
        response = view(self.request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Project Implementation')
        self.assertEqual(response.data['created_by'], self.user.pk)

    def test_create_milestone_json(self):
        data = {'name': 'Project Implementation'}
        self.request = APIRequestFactory().post(
            '/milestone/', json.dumps(data),
            content_type='application/json')
        self.request.user = self.user
        view = MilestoneViewSet.as_view({'post': 'create'})
        response = view(self.request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], u'Project Implementation')
        self.assertEqual(response.data['created_by'], self.user.pk)
