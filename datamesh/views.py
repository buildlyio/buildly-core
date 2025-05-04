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


class LogicModuleModelViewSet(viewsets.ModelViewSet):
    queryset = LogicModuleModel.objects.all()
    serializer_class = LogicModuleModelSerializer


class RelationshipViewSet(viewsets.ModelViewSet):
    queryset = Relationship.objects.all()
    serializer_class = RelationshipSerializer


class JoinRecordViewSet(OrganizationQuerySetMixin, viewsets.ModelViewSet):

    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = JoinRecordFilter
