from django.db.models.signals import post_save
from django.dispatch import receiver

from workflow.models import Organization, CoreGroup, PERMISSIONS_ORG_ADMIN


@receiver(post_save, sender=Organization)
def create_admin_group(sender, instance, **kwargs):
    CoreGroup.objects.get_or_create(
        organization=instance,
        is_org_level=True,
        defaults={'name': 'Organization Admin ({instance.name})', 'permissions': PERMISSIONS_ORG_ADMIN}
    )
