from rest_framework import viewsets
from rest_framework.response import Response

from core.models import CoreGroup
from core.serializers import CoreGroupSerializer
from core.permissions import IsOrgMember


class CoreGroupViewSet(viewsets.ModelViewSet):
    """
    CoreGroup is similar to Django Group, but it is associated with an organization.
    It's used for creating groups of Core Users inside an organization and defining model level permissions
    for this group
    """

    queryset = CoreGroup.objects.all()
    serializer_class = CoreGroupSerializer
    permission_classes = (IsOrgMember,)

    def list(self, request, *args, **kwargs):

        queryset = self.get_queryset()
        if not request.user.is_global_admin:
            # TODO: Shall user also view global groups?
            queryset = queryset.filter(organization_id=request.user.organization_id)
        return Response(self.get_serializer(queryset, many=True).data)

    def perform_create(self, serializer):
        """ override this method to set organization from request """
        organization = self.request.user.organization
        serializer.save(organization=organization)
