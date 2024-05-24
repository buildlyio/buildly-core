from rest_framework import viewsets, filters

from workflow.models import WorkflowLevelType
from workflow.pagination import DefaultCursorPagination
from workflow.serializers import WorkflowLevelTypeSerializer


class WorkflowLevelTypeViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level Type keeps dynamic Types for Workflowlevel2s.

    description:
    A Workflow Level Type has a name and can be related to workflowlevels.

    retrieve:
    Return the given workflowleveltype.

    Return the given workflowleveltype.

    list:
    Return a list of all the existing workflowleveltypes.

    Return a list of all the existing workflowleveltypes.

    create:
    Create a new workflowleveltype instance.

    Create a new workflowleveltype instance.

    update:
    Update the workflowleveltype instance.

    Update the workflowleveltype instance.

    partial_update:
    Update the workflowleveltype instance partially.

    Update the workflowleveltype instance partially.

    destroy:
    Delete the workflowleveltype instance.

    Delete the workflowleveltype instance.
    """

    queryset = WorkflowLevelType.objects.all()
    ordering = ('create_date',)
    filter_backends = (filters.OrderingFilter,)
    serializer_class = WorkflowLevelTypeSerializer
    pagination_class = DefaultCursorPagination
