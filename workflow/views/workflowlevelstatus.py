from rest_framework import viewsets, filters

from workflow.models import WorkflowLevelStatus
from workflow.pagination import DefaultLimitOffsetPagination
from workflow.serializers import WorkflowLevelStatusSerializer


class WorkflowLevelStatusViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level Status keeps dynamic Statuses for Workflowlevel2s.

    description:
    A Workflow Level Status has a name and can be related to workflowlevels.

    retrieve:
    Return the given WorkflowlevelStatus.

    Return the given WorkflowlevelStatus.

    list:
    Return a list of all existing WorkflowlevelStatuses.

    Return a list of all existing WorkflowlevelStatuses.

    create:
    Create a new WorkflowlevelStatus instance.

    Create a new WorkflowlevelStatus instance.

    update:
    Update the WorkflowlevelStatus instance.

    Update the WorkflowlevelStatus instance.

    partial_update:
    Update the WorkflowlevelStatus instance partially.

    Update the WorkflowlevelStatus instance partially.

    destroy:
    Delete the WorkflowlevelStatus instance.

    Delete the WorkflowlevelStatus instance.
    """

    queryset = WorkflowLevelStatus.objects.all()
    ordering = ('order',)
    filter_backends = (filters.OrderingFilter,)
    serializer_class = WorkflowLevelStatusSerializer
    pagination_class = DefaultLimitOffsetPagination
