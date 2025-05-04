import logging
import stripe

from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny


logger = logging.getLogger(__name__)


class StripeViewSet(viewsets.GenericViewSet):
    """
    Products available on the stripe account.

    title:
    Products is a collection of all the products available on the stripe account.

    description:
    All the products available for subscription on the stripe account.

    list:
    Return a list of all the products on the stripe account.
    """

    queryset = []

    # /stripe/products/
    # send all the products
    @action(detail=False, methods=['get'], permission_classes=[AllowAny], name='Fetch all existing products', url_path='products')
    def fetch_existing_products(self, request, pk=None, *args, **kwargs):
        """
        Fetch all existing Products in Stripe Platform
        """
        # all products on stripe platform
        products = []
        if (settings.STRIPE_SECRET):
          stripe.api_key = settings.STRIPE_SECRET
          stripe_products = stripe.Product.list()
          products = stripe_products.data

        return Response(products)