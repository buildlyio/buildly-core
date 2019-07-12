from rest_framework import viewsets

from datamesh.models import JoinRecord
from datamesh.serializers import JoinRecordSerializer


class JoinRecordViewSet(viewsets.ModelViewSet):

    # ToDo:
    #  - add filters for `relationship`, the `record_id/uuid` and `related_record_id/uuid`-fields
    #  - organization permissions
    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
