# TODO: remove this as a part of permissions cleaning refactoring
from rest_framework import viewsets
from rest_framework.response import Response
import django_filters

from core.models import ROLE_ORGANIZATION_ADMIN
from workflow.models import WorkflowTeam
from workflow.serializers import WorkflowTeamSerializer, WorkflowTeamListFullSerializer
from workflow.permissions import CoreGroupsPermissions


class WorkflowTeamViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Team is the the permissions and access control for each workflow
    in the application core.

    description:
    A Workflow level team associates a user with a Group for permissions and workflow level 1
    for access to the entire workflow.

    retrieve:
    Return the given workflow team.

    list:
    Return a list of all the existing workflow teams.

    create:
    Create a new workflow team instance.
    """

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_superuser:
            if ROLE_ORGANIZATION_ADMIN in request.user.groups.values_list(
                'name', flat=True
            ):
                organization_id = request.user.organization_id
                queryset = queryset.filter(
                    workflow_user__organization_id=organization_id
                )
            else:
                wflvl1_ids = WorkflowTeam.objects.filter(
                    workflow_user=request.user
                ).values_list('workflowlevel1__id', flat=True)
                queryset = queryset.filter(workflowlevel1__in=wflvl1_ids)

        nested = request.GET.get('nested_models')
        if nested is not None and (nested.lower() == 'true' or nested == '1'):
            self.serializer_class = WorkflowTeamListFullSerializer

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    filterset_fields = ('workflowlevel1__organization__organization_uuid',)
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (CoreGroupsPermissions,)
    queryset = WorkflowTeam.objects.all()
    serializer_class = WorkflowTeamSerializer
