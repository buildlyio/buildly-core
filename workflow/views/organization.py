import logging

import django_filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from chargebee import Plan, Subscription

from workflow.models import Organization
from workflow.serializers import OrganizationSerializer
from workflow.permissions import IsOrgMember


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
            queryset = queryset.filter(id=organization_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True)
    def subscription(self, request, pk):
        instance = self.get_object()
        try:
            result = Subscription.retrieve(instance.subscription_id)
            subscription = result.subscription
            result = Plan.retrieve(subscription.plan_id)
            plan = result.plan
        except Exception as e:
            logger.warning(e)
            return Response(
                {'detail': 'No subscription was found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            data = {
                'plan': {
                    'name': plan.name,
                },
                'status': subscription.status,
                'total_seats': subscription.plan_quantity,
                'used_seats': instance.used_seats
            }

            return Response(data, status=status.HTTP_200_OK)

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsOrgMember,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
