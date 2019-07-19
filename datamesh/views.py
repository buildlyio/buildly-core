from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets

from .filters import JoinRecordFilter
from .mixins import OrganizationQuerySetMixin
from .models import JoinRecord
from .serializers import JoinRecordSerializer


class JoinRecordViewSet(OrganizationQuerySetMixin,
                        viewsets.ModelViewSet):

    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = JoinRecordFilter
    filter_fields = ('relationship__key',
                     'record_id',
                     'record_uuid',
                     'related_record_id',
                     'related_record_uuid',)
