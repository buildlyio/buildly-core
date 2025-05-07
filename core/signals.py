from django.dispatch import receiver
from django.db.models.signals import post_save

from core.helpers import StripeHelper
from core.models import Coupon


@receiver(post_save, sender=Coupon)
def create_coupon_on_stripe(sender, instance, created, **kwargs):
    # only run this if the instance is created
    if created:
        # generate code
        if not instance.save:
            instance.generate_code()

        # create the coupon on stripe
        stripe_helper = StripeHelper()
        coupon = stripe_helper.create_coupon(instance)

        # update the coupon to set the stripe_coupon_id (Specify the field to update to avoid updating all fields)
        instance.stripe_coupon_id = coupon.id
        instance.save(update_fields=['stripe_coupon_id'])
