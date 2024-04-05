from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import JoinRecordFilter
from .mixins import OrganizationQuerySetMixin
from .models import JoinRecord, LogicModuleModel, Relationship
from .serializers import (
    JoinRecordSerializer,
    LogicModuleModelSerializer,
    RelationshipSerializer,
)
from workflow.permissions import IsSuperUserOrReadOnly


class LogicModuleModelViewSet(viewsets.ModelViewSet):
    queryset = LogicModuleModel.objects.all()
    serializer_class = LogicModuleModelSerializer
    permission_classes = (IsSuperUserOrReadOnly,)


class RelationshiplViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer
    permission_classes = (IsSuperUserOrReadOnly,)


class JoinRecordViewSet(OrganizationQuerySetMixin, viewsets.ModelViewSet):

    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = JoinRecordFilter
    filter_fields = (
        'relationship__key',
        'record_id',
        'record_uuid',
        'related_record_id',
        'related_record_uuid',
    )
