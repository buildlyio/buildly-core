from django.test import TestCase
import factories
from rest_framework.test import APIRequestFactory

from core.views import OrganizationViewSet


class OrganizationListViewTest(TestCase):
    def setUp(self):
        factories.Organization.create()
        factories.Organization.create(name='Another org')

        factory = APIRequestFactory()
        self.request = factory.get('/organization/')

    def test_list_organization_superuser(self):
        self.request.user = factories.CoreUser(is_superuser=True, is_staff=True)
        view = OrganizationViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_organization_normaluser_one_result(self):
        self.request.user = factories.CoreUser()
        view = OrganizationViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_organization_names(self):
        factory = APIRequestFactory()
        self.request = factory.get('/organization/fetch_orgs/')
        self.request.user = factories.CoreUser()

        view = OrganizationViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
