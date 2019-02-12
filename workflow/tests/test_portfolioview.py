import json

from django.test import TestCase
import factories
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from workflow.models import (ROLE_ORGANIZATION_ADMIN, ROLE_PROGRAM_ADMIN,
                             ROLE_PROGRAM_TEAM, ROLE_VIEW_ONLY, Portfolio)

from ..views import PortfolioViewSet


class PortfolioListViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        self.portfolio = factories.Portfolio()

    def test_list_portfolio_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['name'], self.portfolio.name)
        self.assertEqual(response.data[0]['description'],
                         self.portfolio.description)
        self.assertEqual(response.data[0]['organization'],
                         self.portfolio.organization.pk)

    def test_list_portfolio_org_admin_same_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        self.assertEqual(response.data[0]['name'], self.portfolio.name)
        self.assertEqual(response.data[0]['description'],
                         self.portfolio.description)
        self.assertEqual(response.data[0]['organization'],
                         self.core_user.organization.pk)

    def test_list_portfolio_org_admin_different_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)
        organization = factories.Organization(name='Another Org')
        portfolio = factories.Portfolio(organization=organization)

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_portfolio_program_admin(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=factories.WorkflowLevel1(
                organization=self.core_user.organization),
            role=factories.Group(name=ROLE_PROGRAM_ADMIN))

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_portfolio_program_team(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=factories.WorkflowLevel1(
                organization=self.core_user.organization),
            role=factories.Group(name=ROLE_PROGRAM_TEAM))

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_portfolio_view_only(self):
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            workflowlevel1=factories.WorkflowLevel1(
                organization=self.core_user.organization),
            role=factories.Group(name=ROLE_VIEW_ONLY))

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_list_portfolio_other_user(self):
        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.get('')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


class PortfolioCreateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_create_portfolio_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        data = {'name': 'New portfolio',
                'organization': factories.Organization().pk}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        portfolio = Portfolio.objects.values('name', 'organization').get(
            pk=response.data['id'])
        self.assertEqual(portfolio['name'], data['name'])
        self.assertEqual(portfolio['organization'],
                         self.core_user.organization.pk)

    def test_create_portfolio_org_admin(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        data = {'name': 'New portfolio'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        portfolio = Portfolio.objects.values('name', 'organization').get(
            pk=response.data['id'])
        self.assertEqual(portfolio['name'], data['name'])
        self.assertEqual(portfolio['organization'],
                         self.core_user.organization.pk)

    def test_create_portfolio_org_admin_json(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        data = {'name': 'New portfolio'}
        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 201)

        portfolio = Portfolio.objects.values('name', 'organization').get(
            pk=response.data['id'])
        self.assertEqual(portfolio['name'], data['name'])
        self.assertEqual(portfolio['organization'],
                         self.core_user.organization.pk)

    def test_create_portfolio_other_user(self):
        role_without_benefits = ROLE_PROGRAM_ADMIN
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            role=factories.Group(name=role_without_benefits))

        data = {'name': 'New portfolio'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'create'})
        response = view(request)
        self.assertEqual(response.status_code, 403)


class PortfolioUpdateViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        self.portfolio = factories.Portfolio()

    def test_update_unexisting_portfolio(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        request = self.factory.post(None, {})
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=288)
        self.assertEqual(response.status_code, 404)

    def test_update_portfolio_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        data = {'name': 'Some name'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEqual(response.status_code, 200)

        name = Portfolio.objects.values_list('name', flat=True).get(
            pk=self.portfolio.pk)
        self.assertEqual(name, 'Some name')

    def test_update_portfolio_org_admin_same_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        data = {'name': 'Some name'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEqual(response.status_code, 200)

        name = Portfolio.objects.values_list('name', flat=True).get(
            pk=self.portfolio.pk)
        self.assertEqual(name, 'Some name')

    def test_update_portfolio_org_admin_same_org_json(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        data = {'name': 'Some name'}
        request = self.factory.post(None, json.dumps(data),
                                    content_type='application/json')
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEqual(response.status_code, 200)

        name = Portfolio.objects.values_list('name', flat=True).get(
            pk=self.portfolio.pk)
        self.assertEqual(name, 'Some name')

    def test_update_portfolio_org_admin_different_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)
        organization = factories.Organization(name='Another Org')
        portfolio = factories.Portfolio(organization=organization)

        data = {'name': 'Some name'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=portfolio.pk)
        self.assertEqual(response.status_code, 403)

    def test_update_portfolio_org_admin_other_user(self):
        role_without_benefits = ROLE_PROGRAM_ADMIN
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            role=factories.Group(name=role_without_benefits))

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        data = {'name': 'Some name'}
        request = self.factory.post(None, data)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'post': 'update'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEqual(response.status_code, 403)


class PortfolioDeleteViewsTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()
        self.portfolio = factories.Portfolio()

    def test_delete_portfolio_superuser(self):
        self.core_user.user.is_staff = True
        self.core_user.user.is_superuser = True
        self.core_user.user.save()

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            Portfolio.DoesNotExist,
            Portfolio.objects.get, pk=self.portfolio.pk)

    def test_delete_portfolio_org_admin_same_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEquals(response.status_code, 204)
        self.assertRaises(
            Portfolio.DoesNotExist,
            Portfolio.objects.get, pk=self.portfolio.pk)

    def test_delete_portfolio_org_admin_different_org(self):
        group_org_admin = factories.Group(name=ROLE_ORGANIZATION_ADMIN)
        self.core_user.user.groups.add(group_org_admin)
        organization = factories.Organization(name='Another Org')
        portfolio = factories.Portfolio(organization=organization)

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=portfolio.pk)
        self.assertEquals(response.status_code, 403)
        Portfolio.objects.get(pk=portfolio.pk)

    def test_delete_portfolio_org_admin_other_user(self):
        role_without_benefits = ROLE_PROGRAM_ADMIN
        factories.WorkflowTeam(
            workflow_user=self.core_user,
            role=factories.Group(name=role_without_benefits))

        self.portfolio.organization = self.core_user.organization
        self.portfolio.save()

        request = self.factory.delete(None)
        request.user = self.core_user.user
        view = PortfolioViewSet.as_view({'delete': 'destroy'})
        response = view(request, pk=self.portfolio.pk)
        self.assertEquals(response.status_code, 403)
        Portfolio.objects.get(pk=self.portfolio.pk)
