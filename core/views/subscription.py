from dateutil import relativedelta

import stripe

from django.conf import settings
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from core.models import Subscription, Coupon
from core.serializers import SubscriptionSerializer, CouponCodeSerializer


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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # Return an empty queryset for unauthenticated users
            return Subscription.objects.none()

        if not hasattr(self.request.user, 'organization'):
            # Return an empty queryset if the user has no organization
            return Subscription.objects.none()

        queryset = (
            super(SubscriptionViewSet, self)
            .get_queryset()
            .filter(organization=self.request.user.organization)
        )

        if int(self.request.query_params.get('cancelled', '0')):
            queryset = queryset.filter(cancelled=True)
        else:
            queryset = queryset.filter(cancelled=False)

        return queryset.order_by('-create_date')

    def create(self, request, *args, **kwargs):
        # check if organization has a coupon
        try:
            coupon = self.request.user.organization.coupon
        except (AttributeError, KeyError):
            coupon = None

        if settings.STRIPE_SECRET:
            stripe.api_key = settings.STRIPE_SECRET
            stripe.api_version = '2022-11-15'
            data = self.get_stripe_details(coupon)
            if data:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

            return Response(
                data,
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

    def update(self, request, *args, **kwargs):
        # validate coupon code
        if 'coupon' in request.data and not hasattr(self, 'is_coupon_valid'):
            return Response(
                dict(
                    code='invalid_coupon',
                    message='Invalid coupon code'
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        cancelled = self.perform_destroy(instance)
        if not cancelled:
            return Response(
                dict(
                    code='stripe_api_error',
                    message='There was an error cancelling subscription',
                ),
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(
            dict(code='subscription_cancelled'),
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_destroy(self, instance):
        # delete the subscription on stripe
        cancelled = self.cancel_subscription_on_stripe(instance)

        if cancelled:
            # delete the subscription
            instance.cancelled = True
            instance.cancelled_date = timezone.now()
            instance.save()
        return cancelled

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        name='Fetch all existing products',
    )
    def stripe_products(self, request, *args, **kwargs):
        """
        Fetch all existing Products in Stripe Platform
        """
        # all products on stripe platform
        products = []
        if settings.STRIPE_SECRET:
            stripe.api_key = settings.STRIPE_SECRET
            stripe.api_version = '2022-11-15'
            try:
                stripe_products = stripe.Product.search(query="active:'true'")
                products = stripe_products.data
            except stripe.error.StripeError as e:
                # Log the error for debugging
                print(f"Stripe error: {e}")

        return Response(
            products,
            status=status.HTTP_200_OK,
        )

    def get_stripe_details(self, coupon=None):
        """
        Get stripe details
        """
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organization'):
            return None

        data = self.request.data.copy()
        product_id = data.get('product')
        payment_method_id = data.pop('card_id', None)

        if not (product_id and payment_method_id):
            return None

        # get stripe product
        stripe_product = stripe.Product.retrieve(product_id)

        try:
            customer = stripe.Customer.create(
                email=self.request.user.email,
                name=str(self.request.user.organization.name).capitalize(),
                coupon=coupon.stripe_coupon_id if coupon else None,
            )
            stripe.PaymentMethod.attach(payment_method_id, customer=customer.id)

            # set default payment method
            customer = stripe.Customer.modify(
                customer.id,
                invoice_settings={
                    'default_payment_method': payment_method_id
                }
            )

            # create subscription:
            stripe_subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[
                    {"price": stripe_product.default_price},
                ],
            )

            if stripe_subscription:
                stripe_subscription_details = dict(
                    stripe_customer_id=customer.id,
                    stripe_subscription_id=stripe_subscription.id,
                    stripe_product=product_id,
                    stripe_payment_method_id=payment_method_id,
                    trial_start_date=timezone.now().date(),
                    trial_end_date=timezone.now().date() + relativedelta.relativedelta(months=1),
                    subscription_start_date=timezone.datetime.fromtimestamp(
                        stripe_subscription.current_period_start, timezone.utc
                    ).date(),
                    subscription_end_date=timezone.datetime.fromtimestamp(
                        stripe_subscription.current_period_end, timezone.utc
                    ).date(),
                    organization=self.request.user.organization.organization_uuid,
                )
                data.update(stripe_subscription_details)

                data.update(
                    dict(
                        stripe_product_info=dict(
                            id=stripe_product.get('id'),
                            name=stripe_product.get('name'),
                            description=stripe_product.get('description', ''),
                        )
                    )
                )

        except stripe.error.InvalidRequestError:
            return None

        return data

    @staticmethod
    def cancel_subscription_on_stripe(instance):
        """
        Cancel a subscription
        """
        if settings.STRIPE_SECRET:
            stripe.api_key = settings.STRIPE_SECRET
            try:
                subscription = stripe.Subscription.retrieve(instance.stripe_subscription_id)
                subscription.delete()
                return True
            except stripe.error.StripeError as e:
                # Log the error for debugging
                print(f"Stripe error: {e}")
        return False


class CouponCodeViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponCodeSerializer