from chargebee import APIError
from chargebee import Plan, Subscription
from django.test import TestCase
from unittest.mock import Mock
import factories
from rest_framework.test import APIRequestFactory

from ..views import OrganizationViewSet


class OrganizationListViewTest(TestCase):
    def setUp(self):
        factories.Organization.create()
        factories.Organization.create(name='Another org')

        factory = APIRequestFactory()
        self.request = factory.get('/organization/')

    def test_list_organization_superuser(self):
        self.request.user = factories.User.create(is_superuser=True,
                                                  is_staff=True)
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


class OrganizationSubscriptionViewTest(TestCase):
    class SubscriptionTest:
        def __init__(self, values):
            self.subscription = Subscription(values)
            self.subscription.status = 'active'
            self.subscription.plan_quantity = 1

    class PlanTest:
        def __init__(self, values):
            self.plan = Plan(values)
            self.plan.name = values['name']

    def setUp(self):
        self.factory = APIRequestFactory()
        self.core_user = factories.CoreUser()

    def test_get_subscription(self):
        self.core_user.organization.subscription_id = 12345
        self.core_user.organization.save()

        sub_response = self.SubscriptionTest({})
        plan_response = self.PlanTest({'name': 'Plan test'})
        Subscription.retrieve = Mock(return_value=sub_response)
        Plan.retrieve = Mock(return_value=plan_response)

        request = self.factory.get('')
        request.user = self.core_user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.core_user.organization.pk)
        subscription = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(subscription['status'], 'active')
        self.assertEqual(subscription['used_seats'], 0)
        self.assertEqual(subscription['total_seats'], 1)

    def test_get_subscription_error(self):
        self.core_user.organization.subscription_id = 12345
        self.core_user.organization.save()

        json_obj = {
            'message': "Sorry, we couldn't find that resource",
            'error_code': 500
        }

        sub_response = APIError(404, json_obj)
        Subscription.retrieve = Mock(side_effect=sub_response)

        request = self.factory.get('')
        request.user = self.core_user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.core_user.organization.pk)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No subscription was found.')

    def test_get_subscription_id_exception(self):
        self.core_user.organization.subscription_id = 12345
        self.core_user.organization.save()

        sub_response = Exception("Id is None or empty")
        Subscription.retrieve = Mock(side_effect=sub_response)

        request = self.factory.get('')
        request.user = self.core_user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.core_user.organization.pk)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No subscription was found.')
