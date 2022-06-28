from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, filters
from rest_framework.response import Response
import django_filters

from core.permissions import IsOrgMember
from workflow.filters import WorkflowLevel2Filter
from workflow.models import (
    WorkflowLevel2,
    WorkflowLevel2Sort,
    WorkflowTeam,
    ROLE_ORGANIZATION_ADMIN,
)
from workflow.serializers import WorkflowLevel2Serializer, WorkflowLevel2SortSerializer
from workflow.permissions import CoreGroupsPermissions
from workflow.pagination import DefaultLimitOffsetPagination


class WorkflowLevel2ViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level 2 is the secondary building block for creating relational lists, navigation or generic use case
    objects in the application core.

    description:
    A Workflow level 2 can have one parent workflow level 1 and multiple related workflow
    level 2's and be associated with a specific organization or set for an entire application.

    retrieve:
    Return the given workflow level 2.

    list:
    Return a list of all the existing workflow level 2s.

    create:
    Create a new workflow level 2 instance.
    """

    # Remove CSRF request verification for posts to this API
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(WorkflowLevel2ViewSet, self).dispatch(*args, **kwargs)

    def list(self, request, *args, **kwargs):
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            organization_id = request.user.organization_id
            queryset = queryset.filter(workflowlevel1__organization_id=organization_id)

        all_results = request.GET.get('all')
        if all_results and (all_results.lower() == 'true' or all_results == '1'):
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=getattr(self.request.user, 'core_user', None))

    ordering = ('name',)
    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.OrderingFilter,
    )
    filter_class = WorkflowLevel2Filter
    queryset = WorkflowLevel2.objects.all()
    permission_classes = (CoreGroupsPermissions, IsOrgMember)
    serializer_class = WorkflowLevel2Serializer
    pagination_class = DefaultLimitOffsetPagination


class WorkflowLevel2SortViewSet(viewsets.ModelViewSet):
    """
    title:
    Workflow Level 2 sort is a JSON Array storage for the sort and ordering of workflow levels per organization

    description:
    Sort your workflowlevels in the JSON array. WARNING ensure that the JSON array relationships already exist
    in the workflow level 2 parent_id and Workflow level 1

    retrieve:
    Return the given workflow level 2 sort.

    list:
    Return a list of all the existing workflow level 2 sorts.

    create:
    Create a new workflow level 2 sort instance.
    """

    def list(self, request, *args, **kwargs):
        # TODO: refactor this according to the new permissions model
        # Use this queryset or the django-filters lib will not work
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_global_admin:
            user_groups = request.user.groups.values_list('name', flat=True)
            if ROLE_ORGANIZATION_ADMIN in user_groups:
                organization_id = request.user.organization_id
                queryset = queryset.filter(
                    workflowlevel1__organization_id=organization_id
                )
            else:
                wflvl1_ids = WorkflowTeam.objects.filter(
                    workflow_user=request.user
                ).values_list('workflowlevel1__id', flat=True)
                queryset = queryset.filter(workflowlevel1__in=wflvl1_ids)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    queryset = WorkflowLevel2Sort.objects.all()
    permission_classes = (IsOrgMember,)
    serializer_class = WorkflowLevel2SortSerializer
