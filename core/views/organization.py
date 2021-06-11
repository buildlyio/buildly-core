import logging
from django_filters.rest_framework import DjangoFilterBackend
from core.permissions import IsSuperUser
import django_filters
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from core.models import Organization, OrganizationType
from core.serializers import OrganizationSerializer, OrganizationTypeSerializer
from core.permissions import IsOrgMember
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

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

    @csrf_exempt
    @action(detail=False, methods=['get'], permission_classes=[AllowAny],
            name='Fetch Already existing Organization', url_path='fetch_orgs')
    def fetch_existing_orgs(self, request, pk=None, *args, **kwargs):
        """
        Fetch Already existing Organizations in Buildly Core,
        Any logged in user can access this
        """
        # returns names of existing orgs in Buildly Core as a list
        queryset = Organization.objects.all()
        names = list()
        for record in queryset:
            names.append(record.name)

        return Response(names)


class OrganizationTypeViewSet(viewsets.ModelViewSet):
    """
    Organization type  is associated with an organization which defines type of organization.

    title:
    Organization Type

    description:
    An organization type are custodian and producer

    They are associated with an organization.
    Only admin has access to organization type.

    retrieve:
    Return the  Organization Type.

    list:
    Return a list of all the existing  Organization Types.

    create:
    Create a new Organization Type instance.

    update:
    Update a Organization Type instance.

    delete:
    Delete a Organization Type instance.
    """

    filter_fields = ('name',)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsSuperUser,)
    queryset = OrganizationType.objects.all()
    serializer_class = OrganizationTypeSerializer
