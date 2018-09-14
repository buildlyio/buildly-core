from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory
from workflow.models import WorkflowTeam, ROLE_ORGANIZATION_ADMIN, \
    ROLE_PROGRAM_TEAM, ROLE_PROGRAM_ADMIN, ROLE_VIEW_ONLY

from ..views import ApprovalTypeViewSet


class ApprovalTypeListViewsTest(TestCase):
    def setUp(self):
        factories.Organization(id=1)
        factories.ApprovalType.create_batch(2)
        self.factory = APIRequestFactory()
        self.tola_user = factories.CoreUser()

    def test_list_approvaltype_superuser(self):
        request = self.factory.get('/api/approvaltype/')
        request.user = factories.User.build(is_superuser=True,
                                            is_staff=True)
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_approvaltype_org_admin(self):
        request = self.factory.get('/api/approvaltype/')
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.tola_user.user.groups.add(group_org_admin)

        request.user = self.tola_user.user
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.ApprovalType(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_approvaltype_program_admin(self):
        request = self.factory.get('/api/approvaltype/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))
        request.user = self.tola_user.user
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.ApprovalType(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_approvaltype_program_team(self):
        request = self.factory.get('/api/approvaltype/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_PROGRAM_TEAM))
        request.user = self.tola_user.user
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.ApprovalType(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_approvaltype_view_only(self):
        request = self.factory.get('/api/approvaltype/')
        WorkflowTeam.objects.create(
            workflow_user=self.tola_user,
            role=factories.Group(name=ROLE_VIEW_ONLY))
        request.user = self.tola_user.user
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

        factories.ApprovalType(organization=self.tola_user.organization)
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class ApprovalTypeFilterViewTest(TestCase):
    def setUp(self):
        self.tola_user = factories.CoreUser()
        self.factory = APIRequestFactory()

    def test_filter_approvaltype_superuser(self):
        another_org = factories.Organization(name='Another Org')
        approvaltype1_1 = factories.ApprovalType(
            organization=self.tola_user.organization)
        factories.ApprovalType(
            name='Another Approval Type',
            organization=another_org)

        self.tola_user.user.is_staff = True
        self.tola_user.user.is_superuser = True
        self.tola_user.user.save()

        request = self.factory.get('/api/approvaltype/?organization__id=%s' %
                                   self.tola_user.organization.pk)
        request.user = self.tola_user.user
        view = ApprovalTypeViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], approvaltype1_1.name)
