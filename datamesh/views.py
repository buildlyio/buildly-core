from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from datamesh.models import JoinRecord
from datamesh.serializers import JoinRecordSerializer


class JoinRecordViewSet(mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin,
                        GenericViewSet):

    queryset = JoinRecord.objects.all()
    serializer_class = JoinRecordSerializer
