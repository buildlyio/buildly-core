import stripe

from django.conf import settings

from core.models import Coupon


class StripeHelper:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET
        stripe.api_version = '2022-11-15'
        self.stripe = stripe

    def create_coupon(self, coupon: Coupon):
        """
        creates the coupon on stripe when created in insights
        """
        return self.stripe.Coupon.create(
            name=coupon.name,
            percent_off=coupon.percent_off,
            duration=coupon.duration,
            id=coupon.coupon_uuid,
            currency=coupon.currency,
            max_redemptions=coupon.max_redemptions,
            duration_in_months=coupon.duration_in_months,
        )


