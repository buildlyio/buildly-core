from chargebee import APIError
from chargebee import Plan, Subscription
from django.test import TestCase
from unittest.mock import Mock
import factories
from rest_framework.test import APIRequestFactory

from ..views import OrganizationViewSet


class OrganizationListViewTest(TestCase):
    def setUp(self):
        factories.Organization.create_batch(2)

        factory = APIRequestFactory()
        self.request = factory.get('/api/organization/')

    def test_list_organization_superuser(self):
        self.request.user = factories.User.build(is_superuser=True,
                                                 is_staff=True)
        view = OrganizationViewSet.as_view({'get': 'list'})
        response = view(self.request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_list_organization_normaluser_one_result(self):
        tola_user = factories.CoreUser()
        self.request.user = tola_user.user
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
        self.tola_user = factories.CoreUser()

    def test_get_subscription(self):
        self.tola_user.organization.chargebee_subscription_id = 12345
        self.tola_user.organization.save()

        sub_response = self.SubscriptionTest({})
        plan_response = self.PlanTest({'name': 'Plan test'})
        Subscription.retrieve = Mock(return_value=sub_response)
        Plan.retrieve = Mock(return_value=plan_response)

        request = self.factory.get('')
        request.user = self.tola_user.user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.tola_user.organization.id)
        plan = response.data['plan']
        subscription = response.data

        self.assertEqual(response.status_code, 200)
        self.assertEqual(plan['name'], 'Plan test')
        self.assertEqual(subscription['status'], 'active')
        self.assertEqual(subscription['used_seats'], 0)
        self.assertEqual(subscription['total_seats'], 1)

    def test_get_subscription_error(self):
        self.tola_user.organization.chargebee_subscription_id = 12345
        self.tola_user.organization.save()

        json_obj = {
            'message': "Sorry, we couldn't find that resource",
            'error_code': 500
        }

        sub_response = APIError(404, json_obj)
        Subscription.retrieve = Mock(side_effect=sub_response)

        request = self.factory.get('')
        request.user = self.tola_user.user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.tola_user.organization.id)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No subscription was found.')

    def test_get_subscription_id_exception(self):
        self.tola_user.organization.chargebee_subscription_id = 12345
        self.tola_user.organization.save()

        sub_response = Exception("Id is None or empty")
        Subscription.retrieve = Mock(side_effect=sub_response)

        request = self.factory.get('')
        request.user = self.tola_user.user
        view = OrganizationViewSet.as_view({'get': 'subscription'})
        response = view(request, pk=self.tola_user.organization.id)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No subscription was found.')
