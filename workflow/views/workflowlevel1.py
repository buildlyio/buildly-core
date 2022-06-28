from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets, filters
from rest_framework.response import Response
import django_filters

from core.permissions import IsOrgMember
from workflow.models import WorkflowLevel1
from workflow.serializers import WorkflowLevel1Serializer
from workflow.permissions import CoreGroupsPermissions
from workflow.pagination import DefaultCursorPagination


class WorkflowLevel1ViewSet(viewsets.ModelViewSet):
    """
    Workflow Level 1 is the primary building block for creating relational lists, navigation or generic use case objects
    in the application core.  A Workflow level 1 can have multiple related workflow level 2's and be associated with a
    specific organization or set for an entire application.

    title:
    Workflow Level 1 is the primary building block for creating relationships

    description:
    Workflow Level 1 is the primary building block for creating relational lists, navigation or generic use case objects
    in the application core.  A Workflow level 1 can have multiple related workflow level 2's and be associated with a
    specific organization or set for an entire application.

    retrieve:
    Return the given workflow.

    list:
    Return a list of all the existing workflows.

    create:
    Create a new workflow instance.
    """

    # Remove CSRF request verification for posts to this API
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WorkflowLevel1ViewSet, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            queryset = queryset.filter(organization_id=request.user.organization_id)

        paginate = request.GET.get('paginate')
        if paginate and (paginate.lower() == 'true' or paginate == '1'):
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # inherited from CreateModelMixin
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        organization = self.request.user.organization
        obj = serializer.save(organization=organization)
        obj.user_access.add(self.request.user)

    def destroy(self, request, *args, **kwargs):
        workflowlevel1 = self.get_object()
        workflowlevel1.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    ordering_fields = ('name',)
    ordering = ('name',)
    filterset_fields = ('name', 'level1_uuid')
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    queryset = WorkflowLevel1.objects.all()
    serializer_class = WorkflowLevel1Serializer
    permission_classes = (CoreGroupsPermissions, IsOrgMember)
    pagination_class = DefaultCursorPagination
