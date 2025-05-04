from django_filters import rest_framework as django_filters

from .models import JoinRecord


class JoinRecordFilter(django_filters.FilterSet):

    record_id = django_filters.BaseInFilter()
    record_uuid = django_filters.BaseInFilter()
    related_record_id = django_filters.BaseInFilter()
    related_record_uuid = django_filters.BaseInFilter()

    class Meta:
        model = JoinRecord
        fields = (
            'record_id',
            'record_uuid',
            'related_record_id',
            'related_record_uuid',
        )
