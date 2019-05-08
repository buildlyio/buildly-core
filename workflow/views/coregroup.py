from rest_framework import viewsets

from workflow.models import CoreGroup
from workflow.serializers import CoreGroupSerializer
from workflow.permissions import CoreGroupsPermissions


class CoreGroupViewSet(viewsets.ModelViewSet):
    """
    CoreGroup is similar to Django Group, but it is associated with an organization.
    It's used for creating groups of Core Users inside an organization and defining model level permissions
    for this group
    """
    queryset = CoreGroup.objects.all()
    serializer_class = CoreGroupSerializer
    permission_classes = (CoreGroupsPermissions,)
