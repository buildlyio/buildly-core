import logging

import django_filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import Organization
from core.serializers import OrganizationSerializer
from core.permissions import IsOrgMember


logger = logging.getLogger(__name__)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    Organization is a collection of CoreUsers An organization is also the primary relationship for a user.
    They are associated with an organization that then provides them access to join a workflow team.

    title:
    Organization is a collection of CoreUsers

    description:
    An organization is also the primary relationship for a user.
    They are associated with an organization that then provides them access to join a workflow team.

    retrieve:
    Return the given organization user.

    list:
    Return a list of all the organizations.

    create:
    Create a new organization instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            organization_id = request.user.organization_id
            queryset = queryset.filter(pk=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsOrgMember,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    @action(detail=False, methods=['get'], name='Fetch Already existing Organization', url_path='fetch_orgs')
    def fetch_existing_orgs(self, request, pk=None, *args, **kwargs):
        """
        Fetch Already existing Organizations in Buildly Core,
        Any logged in user can access this
        """
        # all orgs in Buildly Core
        queryset = Organization.objects.all()
        serializer = OrganizationSerializer(queryset, many=True)
        return Response(serializer.data)
