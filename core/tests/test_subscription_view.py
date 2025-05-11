from django.urls import reverse
from django.utils import timezone
from django.test import override_settings
from rest_framework import status
from rest_framework.test import (APIClient, APITestCase)

import factories


class SubscriptionTestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = factories.CoreUser(
            first_name='John', last_name='doe', email="john@gmail.com"
        )
        self.subscription = factories.Subscription(
            subscription_start_date=timezone.localdate(),
            organization=self.user.organization
        )

    def test_list_subscriptions(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(
            reverse('subscription-list')
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # @override_settings(STRIPE_SECRET='sk_test_ddLjeqLRWcj8znVAhMaNPu7J00evbJrikA')
    # def test_post_subscription(self):
    #     self.client.force_authenticate(self.user)
    #     payload = dict(
    #         product='pm_1MQveB2eZvKYlo2CNDz1tA9f',
    #         stripe_card_info='card_1MQtzn2eZvKYlo2C8conuf6j'
    #     )
    #
    #     response = self.client.post(
    #         reverse('subscription-list'),
    #         payload,
    #         format='json'
    #     )
    #     self.assertEqual(response.status_code, (status.HTTP_201_CREATED or status.HTTP_400_BAD_REQUEST))
    #     self.assertEqual(response.data.get('product'), 'prod_LcvzgZTikSo1yd')

    def test_get_stripe_products(self):
        response = self.client.get(f'{reverse("subscription-list")}stripe_products/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)
