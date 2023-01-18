import logging
from datetime import datetime
from dateutil import relativedelta

import stripe

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import (AllowAny, IsAuthenticated)

from core.models import Subscription
from core.serializers import SubscriptionSerializer


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
     Managing subscriptions

     title:
     Manage user subscription done through stripe

     description:
     All the subscriptions related actions

     """
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = (AllowAny, IsAuthenticated)

    def create(self, request, *args, **kwargs):
        if settings.STRIPE_SECRET:
            data = self.get_stripe_details()
            if data:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        return Response(
            dict(
                code='missing_stripe_details',
                message='Please pass valid product/card or stripe secret'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if settings.STRIPE_SECRET:
            data = self.get_stripe_details()
            if data:
                serializer = self.get_serializer(instance, data=data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

        return Response(
            dict(
                code='missing_stripe_details',
                message='Please pass valid product/card or stripe secret'
            ),
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            created_by=self.request.user,
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[AllowAny],
        name='Fetch all existing products',
    )
    def stripe_products(self, request, pk=None, *args, **kwargs):
        """
        Fetch all existing Products in Stripe Platform
        """
        # all products on stripe platform
        products = []
        if settings.STRIPE_SECRET:
            stripe.api_key = settings.STRIPE_SECRET
            stripe_products = stripe.Product.list()
            products = stripe_products.data

        return Response(
            products,
            status=status.HTTP_200_OK,
        )

    def get_stripe_details(self):
        """
        Get stripe details
        """
        data = self.request.data.copy()
        product = data.get('product')
        card_id = data.pop('card_id', None)

        if not (product and card_id):
            return None

        try:
            stripe.api_key = settings.STRIPE_SECRET
            customer = stripe.Customer.create(
                email=self.request.user.email,
                name=str(self.request.user.organization.name).capitalize()
            )
            stripe.PaymentMethod.attach(card_id, customer=customer.id)
            stripe_subscription_details = dict(
                customer_stripe_id=customer.id,
                stripe_product=product,
                stripe_card_id=card_id,
                trial_start_date=timezone.now().date(),
                trial_end_date=timezone.now().date() + relativedelta.relativedelta(months=1),
                subscription_start_date=timezone.now().date() + relativedelta.relativedelta(months=1),
                organization=self.request.user.organization.id,
            )

            data.update(stripe_subscription_details)
        except stripe.error.InvalidRequestError:
            return None

        return data
